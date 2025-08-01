"""
OpenAI API client implementation
"""

from openai import OpenAI
from typing import Dict, Any, Optional
from ..utils.logger import get_logger


class OpenAIClient:
    """
    OpenAI API client for ESKAI framework.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.logger = get_logger("OpenAIClient")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature or self.temperature,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def classify_intent(self, prompt: str) -> str:
        """
        Classify intent using OpenAI.
        
        Args:
            prompt: Input prompt to classify
            
        Returns:
            Classification result as JSON string
        """
        classification_prompt = f"""
        Classify the following user input as either "chat" or "objective":
        
        Input: "{prompt}"
        
        Return only a JSON object with:
        - intent: "chat" or "objective"
        - confidence: number between 0 and 1
        - reasoning: brief explanation
        """
        
        response = self.generate_response(
            classification_prompt,
            max_tokens=150,
            temperature=0.1
        )
        
        return response
    
    def extract_objectives(self, prompt: str) -> str:
        """
        Extract objectives from user prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Extracted objectives
        """
        objectives_prompt = f"""
        Extract clear, actionable objectives from this user request:
        
        Request: "{prompt}"
        
        Return a JSON object with:
        - primary_objectives: list of main objectives
        - secondary_objectives: list of supporting objectives
        - expected_outcomes: list of expected results
        - constraints: list of limitations or requirements
        """
        
        return self.generate_response(
            objectives_prompt,
            max_tokens=500,
            temperature=0.3
        )
    
    def generate_workflow(self, objectives_data: Dict[str, Any]) -> str:
        """
        Generate workflow from objectives.
        
        Args:
            objectives_data: Structured objectives data
            
        Returns:
            Generated workflow
        """
        workflow_prompt = f"""
        Create a detailed workflow to achieve these objectives:
        
        Objectives: {objectives_data}
        
        Return a JSON object with:
        - workflow_id: unique identifier
        - steps: list of workflow steps with dependencies
        - critical_path: list of critical steps
        - parallel_groups: groups of steps that can run in parallel
        """
        
        return self.generate_response(
            workflow_prompt,
            max_tokens=1000,
            temperature=0.3
        )
    
    def synthesize_results(self, agent_outputs: list, original_objectives: Dict[str, Any]) -> str:
        """
        Synthesize results from multiple agents.
        
        Args:
            agent_outputs: List of agent outputs
            original_objectives: Original objectives data
            
        Returns:
            Synthesized result
        """
        synthesis_prompt = f"""
        Synthesize these agent outputs into a coherent final result:
        
        Original Objectives: {original_objectives}
        Agent Outputs: {agent_outputs}
        
        Provide a comprehensive synthesis that addresses all objectives.
        """
        
        return self.generate_response(
            synthesis_prompt,
            max_tokens=2000,
            temperature=0.4
        )
