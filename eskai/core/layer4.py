"""
Layer 4: Agent Orchestration
Transforms workflows into executable agent specifications.
"""

from typing import Dict, Any
from ..utils.logger import get_logger


class AgentOrchestrator:
    """
    Orchestrates agents from work plans.
    """
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.logger = get_logger("AgentOrchestrator", level=config.log_level)
    
    def orchestrate_agents(
        self,
        work_plan: Dict[str, Any],
        enable_internet: bool = True,
        enable_code_execution: bool = True
    ) -> Dict[str, Any]:
        """
        Create agent orchestration from work plan.
        
        Args:
            work_plan: Work plan from Layer 3
            enable_internet: Whether to enable internet access
            enable_code_execution: Whether to enable code execution
            
        Returns:
            Agent orchestration plan
        """
        self.logger.info("Orchestrating agents from work plan")
        
        agents = []
        execution_phases = []
        
        # Create agents from work plan steps
        for step in work_plan["steps"]:
            agent = {
                "agent_id": f"agent_{step['step_id']}",
                "agent_name": f"Agent for {step['description']}",
                "agent_type": "executor",
                "system_prompt": "You are a helpful AI agent executing tasks.",
                "input_prompt": step["description"],
                "model": "gpt-4",
                "tools": step["required_tools"] if enable_internet else [],
                "dependencies": step["dependencies"],
                "parallel_group": step["parallel_group"],
                "timeout": "1800",
                "retry_policy": "retry_3",
                "output_format": "text"
            }
            agents.append(agent)
        
        # Create execution phases
        execution_phases.append({
            "phase_id": "phase_1",
            "agents": [agent["agent_id"] for agent in agents],
            "execution_type": "sequential",
            "dependencies": []
        })
        
        orchestration = {
            "agents": agents,
            "execution_order": [agent["agent_id"] for agent in agents],
            "orchestration_plan": {
                "execution_phases": execution_phases,
                "resource_allocation": {
                    "max_concurrent_agents": self.config.max_concurrent_agents,
                    "resource_limits": "standard"
                }
            }
        }
        
        self.logger.info(f"Orchestrated {len(agents)} agents")
        return orchestration
