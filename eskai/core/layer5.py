"""
Layer 5: Execution Engine
Executes agents according to orchestration plan with monitoring.
"""

import time
from typing import Dict, Any
from ..utils.logger import get_logger


class ExecutionEngine:
    """
    Executes agent orchestration plans with comprehensive monitoring.
    """
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.logger = get_logger("ExecutionEngine", level=config.log_level)
    
    def execute_orchestration_plan(
        self,
        orchestration: Dict[str, Any],
        max_execution_time: int = 3600
    ) -> Dict[str, Any]:
        """
        Execute the orchestration plan.
        
        Args:
            orchestration: Agent orchestration plan
            max_execution_time: Maximum execution time in seconds
            
        Returns:
            Execution results
        """
        self.logger.info("Starting agent execution")
        
        start_time = time.time()
        execution_results = {
            "execution_id": f"exec_{int(start_time)}",
            "start_time": start_time,
            "agent_results": {},
            "performance_metrics": {},
            "status": "running"
        }
        
        # Execute agents
        for agent in orchestration["agents"]:
            agent_start = time.time()
            
            try:
                self.logger.info(f"Executing agent: {agent['agent_id']}")
                
                # Get provider for agent execution
                provider = self.provider_manager.get_primary_provider()
                
                # Execute agent task
                result = provider.generate_response(
                    agent["input_prompt"],
                    max_tokens=1000
                )
                
                agent_duration = time.time() - agent_start
                
                execution_results["agent_results"][agent["agent_id"]] = {
                    "status": "completed",
                    "output": result,
                    "duration": agent_duration,
                    "tools_used": agent.get("tools", []),
                    "model": agent.get("model", "unknown")
                }
                
                self.logger.info(f"Agent {agent['agent_id']} completed in {agent_duration:.2f}s")
                
            except Exception as e:
                self.logger.error(f"Agent {agent['agent_id']} failed: {str(e)}")
                execution_results["agent_results"][agent["agent_id"]] = {
                    "status": "failed",
                    "error": str(e),
                    "duration": time.time() - agent_start
                }
        
        # Calculate final metrics
        total_duration = time.time() - start_time
        successful_agents = sum(1 for r in execution_results["agent_results"].values() if r["status"] == "completed")
        total_agents = len(orchestration["agents"])
        
        execution_results.update({
            "end_time": time.time(),
            "total_duration": total_duration,
            "performance_metrics": {
                "total_agents": total_agents,
                "successful_agents": successful_agents,
                "success_rate": successful_agents / total_agents if total_agents > 0 else 0,
                "average_agent_duration": sum(r.get("duration", 0) for r in execution_results["agent_results"].values()) / total_agents if total_agents > 0 else 0
            },
            "status": "completed"
        })
        
        self.logger.info(f"Execution completed in {total_duration:.2f}s with {successful_agents}/{total_agents} successful agents")
        
        return execution_results
