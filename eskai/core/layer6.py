"""
Layer 6: Final Result Rendering
Synthesizes execution results into coherent final output.
"""

from typing import Dict, Any, List
from ..utils.logger import get_logger


class ResultRenderer:
    """
    Renders final results from execution data.
    """
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.logger = get_logger("ResultRenderer", level=config.log_level)
    
    def render_final_result(
        self,
        execution_results: Dict[str, Any],
        original_objectives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render final result from execution data.
        
        Args:
            execution_results: Results from Layer 5 execution
            original_objectives: Original objectives from Layer 2
            
        Returns:
            Final rendered result
        """
        self.logger.info("Rendering final results")
        
        # Collect all agent outputs
        agent_outputs = []
        for agent_id, result in execution_results["agent_results"].items():
            if result["status"] == "completed":
                agent_outputs.append({
                    "agent_id": agent_id,
                    "output": result["output"],
                    "tools_used": result.get("tools_used", [])
                })
        
        # Synthesize results
        try:
            provider = self.provider_manager.get_primary_provider()
            
            synthesis_prompt = f"""
            Synthesize the following agent outputs into a comprehensive final result:
            
            Original Objectives: {original_objectives["primary_objectives"]}
            
            Agent Outputs:
            {self._format_agent_outputs(agent_outputs)}
            
            Provide a coherent, comprehensive response that addresses all the original objectives.
            """
            
            synthesized_result = provider.generate_response(
                synthesis_prompt,
                max_tokens=2000
            )
            
        except Exception as e:
            self.logger.warning(f"Synthesis failed, using fallback: {str(e)}")
            synthesized_result = self._fallback_synthesis(agent_outputs, original_objectives)
        
        # Validate against objectives
        objective_alignment = self._validate_against_objectives(
            synthesized_result,
            original_objectives
        )
        
        final_result = {
            "final_result": synthesized_result,
            "objective_alignment": objective_alignment,
            "completeness_score": self._calculate_completeness_score(agent_outputs, original_objectives),
            "supporting_evidence": agent_outputs,
            "execution_summary": {
                "total_agents": len(execution_results["agent_results"]),
                "successful_agents": len(agent_outputs),
                "total_duration": execution_results.get("total_duration", 0),
                "success_rate": execution_results["performance_metrics"]["success_rate"]
            }
        }
        
        self.logger.info(f"Final result rendered with completeness score: {final_result['completeness_score']:.2f}")
        
        return final_result
    
    def _format_agent_outputs(self, agent_outputs: List[Dict[str, Any]]) -> str:
        """Format agent outputs for synthesis."""
        formatted = []
        for i, output in enumerate(agent_outputs, 1):
            formatted.append(f"Agent {i} Output: {output['output']}")
        return "\n\n".join(formatted)
    
    def _fallback_synthesis(
        self,
        agent_outputs: List[Dict[str, Any]],
        original_objectives: Dict[str, Any]
    ) -> str:
        """Fallback synthesis when provider fails."""
        if not agent_outputs:
            return "No results were generated due to execution failures."
        
        summary = f"Summary based on {len(agent_outputs)} agent executions:\n\n"
        
        for i, output in enumerate(agent_outputs, 1):
            summary += f"Result {i}: {output['output']}\n\n"
        
        summary += f"\nObjectives addressed: {', '.join(original_objectives['primary_objectives'])}"
        
        return summary
    
    def _validate_against_objectives(
        self,
        result: str,
        objectives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate result against original objectives."""
        
        # Simple keyword-based validation
        result_lower = result.lower()
        objectives_met = []
        
        for obj in objectives["primary_objectives"]:
            # Simple heuristic: check if key words from objective appear in result
            obj_words = obj.lower().split()
            found_words = sum(1 for word in obj_words if word in result_lower)
            
            alignment_score = found_words / len(obj_words) if obj_words else 0
            
            objectives_met.append({
                "objective": obj,
                "alignment_score": alignment_score,
                "status": "addressed" if alignment_score > 0.3 else "partial"
            })
        
        overall_alignment = sum(obj["alignment_score"] for obj in objectives_met) / len(objectives_met) if objectives_met else 0
        
        return {
            "overall_alignment_score": overall_alignment,
            "objectives_assessment": objectives_met,
            "fully_addressed": sum(1 for obj in objectives_met if obj["status"] == "addressed"),
            "total_objectives": len(objectives["primary_objectives"])
        }
    
    def _calculate_completeness_score(
        self,
        agent_outputs: List[Dict[str, Any]],
        objectives: Dict[str, Any]
    ) -> float:
        """Calculate completeness score based on outputs and objectives."""
        
        if not agent_outputs:
            return 0.0
        
        # Factors: number of successful agents, total output length, objective coverage
        output_factor = len(agent_outputs) / max(len(objectives["primary_objectives"]), 1)
        
        total_output_length = sum(len(output["output"]) for output in agent_outputs)
        length_factor = min(1.0, total_output_length / 1000)  # Normalize to 1000 chars
        
        # Combine factors
        completeness = (output_factor * 0.6 + length_factor * 0.4)
        
        return min(1.0, completeness)
