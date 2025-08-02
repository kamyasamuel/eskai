"""
Gemini API client implementation
"""

from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from google import genai
from google.genai import types


class GeminiClient:
    """
    Gemini API client for ESKAI framework.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = genai.Client(api_key=self.api_key)
        self.logger = get_logger("GeminiClient")
    
    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        **kwargs
    ) -> str:
        """
        Generate response using Gemini API.
        """
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            ),
            contents=prompt
        )
        return response.text.strip() if response.text is not None else ""
    
    def classify_intent(self, prompt: str) -> str:
        """Classify intent using Gemini. Return JSON string with intent, confidence, and reasoning."""
        response = self.generate_response(
            prompt=prompt,
            system_instruction=(
            "You are an expert intent classification system. "
            "Analyze the user's message and determine their intent as accurately as possible. "
            "Respond ONLY in valid JSON format with the following keys: "
            "'intent' (a concise label for the user's intent), "
            "'confidence' (a float between 0 and 1 representing your confidence in the classification), "
            "and 'reasoning' (a brief explanation for your classification). "
            "Do not include any extra text or formatting outside the JSON object."
            )
        )
        return response

    def extract_objectives(self, prompt: str) -> str:
        """Extract objectives using Gemini."""
        """
        Generate response using Gemini API.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an expert at extracting objectives from user input. "
                        "Analyze the user's message and identify their primary and secondary objectives. "
                        "Respond ONLY in valid JSON format with the following keys: "
                        "'primary_objectives' (a list of the main objectives), "
                        "'secondary_objectives' (a list of any secondary objectives). "
                        "Do not include any extra text or formatting outside the JSON object."
                    )
                ),
                contents=prompt
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return ""
        # return '{"primary_objectives": ["gemini_objective"], "secondary_objectives": []}'

    def generate_workflow(self, objectives_data: Dict[str, Any]) -> str:
        """Generate workflow using Gemini."""
        try:
            prompt = f"Based on these objectives: {objectives_data}, create a detailed workflow."
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an expert workflow designer. "
                        "Create a detailed workflow based on the provided objectives. "
                        "Respond ONLY in valid JSON format with the following structure: "
                        "'workflow_id' (a unique identifier), "
                        "'steps' (a list of workflow steps with id, description, type, dependencies, etc.), "
                        "'critical_path' (list of critical step IDs), "
                        "'parallel_groups' (groups of steps that can run in parallel). "
                        "Do not include any extra text or formatting outside the JSON object."
                    )
                ),
                contents=prompt
            )
            return response.text.strip() if response.text else '{"workflow_id": "gemini_workflow", "steps": []}'
        except Exception as e:
            self.logger.error(f"Error generating workflow: {e}")
            return '{"workflow_id": "gemini_workflow", "steps": []}'
    
    def synthesize_results(self, agent_outputs: list, original_objectives: Dict[str, Any]) -> str:
        """Synthesize results using Gemini."""
        try:
            prompt = f"""
            Synthesize these agent outputs into a coherent final result:
            
            Original Objectives: {original_objectives}
            Agent Outputs: {agent_outputs}
            
            Provide a comprehensive synthesis that addresses all objectives.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an expert at synthesizing multiple pieces of information into coherent results. "
                        "Take the provided agent outputs and original objectives, then create a comprehensive "
                        "final result that addresses all objectives clearly and professionally. "
                        "Focus on clarity, completeness, and actionable insights."
                    )
                ),
                contents=prompt
            )
            return response.text.strip() if response.text else "Gemini synthesis result"
        except Exception as e:
            self.logger.error(f"Error synthesizing results: {e}")
            return "Gemini synthesis result"
