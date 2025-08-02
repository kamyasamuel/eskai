"""
Groq API client implementation
"""

from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class GroqClient:
    """
    Groq API client for ESKAI framework.
    """
    
    def __init__(self, api_key: str, model: str = "qwen/qwen3-32b", temperature: float = 0.7):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
        self.client = Groq(api_key=self.api_key)
        self.logger = get_logger("GroqClient")
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate response using Groq API.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or 4096,
                top_p=0.95
            )
            return completion.choices[0].message.content.strip() if completion.choices[0].message.content else ""
        except Exception as e:
            self.logger.error(f"Groq API error: {str(e)}")
            return f"Groq response for: {prompt[:50]}..."
    
    def classify_intent(self, prompt: str) -> str:
        """Classify intent using Groq."""
        try:
            system_instruction = """
                You are an intent classifier. Analyze the user's prompt and classify it as either 'chat' 
                (simple conversation) or 'objective' (task requiring multi-step execution).
                Return your response in this exact JSON format:
                {
                    "intent": "chat" or "objective",
                    "confidence": float between 0.0 and 1.0,
                    "reasoning": "brief explanation of classification"
                }
            """
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                top_p=0.95
            )
            return completion.choices[0].message.content.strip() if completion.choices[0].message.content else ""
        except Exception as e:
            self.logger.error(f"Groq intent classification error: {str(e)}")
            return '{"intent": "objective", "confidence": 0.8, "reasoning": "Groq classification fallback"}'
    
    def extract_objectives(self, prompt: str) -> str:
        """Extract objectives using Groq."""
        try:
            system_instruction = """
                You are an objective extraction specialist. Analyze the user's prompt and extract clear, 
                actionable objectives.
                Return your response in this exact JSON format:
                {
                    "primary_objectives": ["main goal 1", "main goal 2"],
                    "secondary_objectives": ["supporting goal 1", "supporting goal 2"],
                    "constraints": ["constraint 1", "constraint 2"],
                    "success_criteria": ["criterion 1", "criterion 2"]
                }
            """
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                top_p=0.95
            )
            return completion.choices[0].message.content.strip() if completion.choices[0].message.content else ""
        except Exception as e:
            self.logger.error(f"Groq objective extraction error: {str(e)}")
            return '{"primary_objectives": [], "secondary_objectives": [], "constraints": [], "success_criteria": []}'
    
    def generate_workflow(self, objectives_data: Dict[str, Any]) -> str:
        """Generate workflow using Groq."""
        try:
            system_instruction = """
                You are a workflow generation expert. Based on the provided objectives, create a detailed 
                step-by-step workflow plan.
                Return your response in this exact JSON format:
                {
                    "workflow_id": "unique_workflow_identifier",
                    "steps": [
                        {
                            "step_id": 1,
                            "action": "description of action",
                            "agent_type": "agent type needed",
                            "expected_output": "what this step should produce",
                            "dependencies": []
                        }
                    ],
                    "estimated_duration": "time estimate",
                    "complexity_level": "low/medium/high"
                }
            """
            prompt = f"Generate a workflow for these objectives: {objectives_data}"
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000,
                top_p=0.95
            )
            return completion.choices[0].message.content.strip() if completion.choices[0].message.content else ""
        except Exception as e:
            self.logger.error(f"Groq workflow generation error: {str(e)}")
            return '{"workflow_id": "groq_workflow_fallback", "steps": [], "estimated_duration": "unknown", "complexity_level": "medium"}'
    
    def synthesize_results(self, agent_outputs: list, original_objectives: Dict[str, Any]) -> str:
        """Synthesize results using Groq."""
        try:
            system_instruction = """
                You are a result synthesis expert. Analyze the agent outputs and original objectives to create a 
                comprehensive final result.

                Your response should be a well-structured summary that:
                1. Evaluates how well the objectives were met
                2. Synthesizes key findings from all agent outputs
                3. Identifies any gaps or areas for improvement
                4. Provides actionable next steps if needed

                Return a clear, professional summary."""
                            
            prompt = f"""
                Original Objectives: {original_objectives}

                Agent Outputs: {agent_outputs}

                Please synthesize these results into a comprehensive final report.
                """
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000,
                top_p=0.95
            )
            return completion.choices[0].message.content.strip() if completion.choices[0].message.content else ""
        except Exception as e:
            self.logger.error(f"Groq result synthesis error: {str(e)}")
            return "Groq synthesis result - fallback due to API error"
