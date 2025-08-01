"""
Main ESKAI class - The core AGI framework implementation
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.config import ESKAIConfig
from .layer1 import PromptAssessor
from .layer2 import ObjectiveFormulator
from .layer3 import WorkPlanGenerator
from .layer4 import AgentOrchestrator
from .layer5 import ExecutionEngine
from .layer6 import ResultRenderer
from ..providers.provider_manager import ProviderManager


class ESKAI:
    """
    Main ESKAI AGI Framework class.
    
    Processes user inputs through six layers of sophisticated AI processing
    to deliver comprehensive solutions to complex problems.
    """
    
    def __init__(self, config: Optional[ESKAIConfig] = None):
        """
        Initialize the ESKAI framework.
        
        Args:
            config: Optional configuration object. If None, uses default config.
        """
        self.config = config or ESKAIConfig()
        self.logger = get_logger("ESKAI", level=self.config.log_level)
        
        # Initialize providers
        self.provider_manager = ProviderManager(self.config)
        
        # Initialize layers
        self.layer1 = PromptAssessor(self.provider_manager, self.config)
        self.layer2 = ObjectiveFormulator(self.provider_manager, self.config)
        self.layer3 = WorkPlanGenerator(self.provider_manager, self.config)
        self.layer4 = AgentOrchestrator(self.provider_manager, self.config)
        self.layer5 = ExecutionEngine(self.provider_manager, self.config)
        self.layer6 = ResultRenderer(self.provider_manager, self.config)
        
        self.logger.info("ESKAI framework initialized successfully")
    
    def process(
        self,
        prompt: str,
        max_execution_time: Optional[int] = None,
        enable_internet: bool = True,
        enable_code_execution: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user prompt through the complete ESKAI pipeline.
        
        Args:
            prompt: The user's input prompt
            max_execution_time: Maximum execution time in seconds
            enable_internet: Whether to enable internet access for agents
            enable_code_execution: Whether to enable code execution
            context: Optional context from previous interactions
            
        Returns:
            Dictionary containing the final result and execution metadata
        """
        execution_id = f"eskai_{int(time.time())}"
        start_time = datetime.now()
        
        self.logger.info(f"Starting ESKAI processing - ID: {execution_id}")
        self.logger.info(f"Prompt: {prompt[:100]}...")
        
        try:
            # Layer 1: Prompt Assessment
            self.logger.info("Layer 1: Assessing prompt intent")
            assessment = self.layer1.assess_intent(prompt, context)
            
            # If it's just chat, return simple response
            if assessment["intent"] == "chat":
                self.logger.info("Chat intent detected - generating simple response")
                chat_response = self._generate_chat_response(prompt)
                return {
                    "type": "chat",
                    "response": chat_response,
                    "execution_id": execution_id,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Layer 2: Objective Formulation
            self.logger.info("Layer 2: Formulating objectives")
            objectives = self.layer2.formulate_objectives(prompt, assessment, context)
            
            # Layer 3: Work Plan Generation
            self.logger.info("Layer 3: Generating work plan")
            work_plan = self.layer3.generate_work_plan(objectives)
            
            # Layer 4: Agent Orchestration
            self.logger.info("Layer 4: Orchestrating agents")
            orchestration = self.layer4.orchestrate_agents(
                work_plan, 
                enable_internet=enable_internet,
                enable_code_execution=enable_code_execution
            )
            
            # Layer 5: Execution
            self.logger.info("Layer 5: Executing agents")
            execution_results = self.layer5.execute_orchestration_plan(
                orchestration,
                max_execution_time=max_execution_time or self.config.default_timeout
            )
            
            # Layer 6: Final Result Rendering
            self.logger.info("Layer 6: Rendering final results")
            final_result = self.layer6.render_final_result(
                execution_results,
                objectives
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "type": "objective",
                "execution_id": execution_id,
                "final_result": final_result,
                "objectives": objectives,
                "work_plan": work_plan,
                "execution_results": execution_results,
                "processing_time": processing_time,
                "success": True
            }
            
            self.logger.info(f"ESKAI processing completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"ESKAI processing failed: {str(e)}")
            
            return {
                "type": "error",
                "execution_id": execution_id,
                "error": str(e),
                "processing_time": processing_time,
                "success": False
            }
    
    def _generate_chat_response(self, prompt: str) -> str:
        """
        Generate a simple chat response for conversational prompts.
        
        Args:
            prompt: The user's chat prompt
            
        Returns:
            A friendly chat response
        """
        try:
            # Use primary provider for simple chat
            provider = self.provider_manager.get_primary_provider()
            
            chat_prompt = f"""
            You are ESKAI, a helpful AI assistant. The user said: "{prompt}"
            
            Provide a friendly, helpful response. Keep it conversational and natural.
            """
            
            response = provider.generate_response(chat_prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"Chat response generation failed: {str(e)}")
            return "Hello! I'm ESKAI, your AI assistant. How can I help you today?"
    
    async def process_async(
        self,
        prompt: str,
        max_execution_time: Optional[int] = None,
        enable_internet: bool = True,
        enable_code_execution: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Asynchronous version of process method.
        
        Args:
            prompt: The user's input prompt
            max_execution_time: Maximum execution time in seconds
            enable_internet: Whether to enable internet access for agents
            enable_code_execution: Whether to enable code execution
            context: Optional context from previous interactions
            
        Returns:
            Dictionary containing the final result and execution metadata
        """
        # Run the synchronous process method in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.process,
            prompt,
            max_execution_time,
            enable_internet,
            enable_code_execution,
            context
        )
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of recent executions.
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of execution metadata
        """
        # This would be implemented with a persistent storage system
        # For now, return empty list
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the ESKAI framework.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "version": "0.1.0",
            "status": "operational",
            "providers": self.provider_manager.get_provider_status(),
            "config": {
                "max_concurrent_agents": self.config.max_concurrent_agents,
                "enable_parallel_execution": self.config.enable_parallel_execution,
                "default_timeout": self.config.default_timeout
            }
        }
