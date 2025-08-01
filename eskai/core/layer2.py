"""
Layer 2: Objective Formulation
Extracts clear, actionable objectives from user input and defines expected outcomes.
"""

import json
from typing import Dict, Any, Optional, List
from ..utils.logger import get_logger


class ObjectiveFormulator:
    """
    Formulates clear objectives from user prompts using multi-provider validation.
    """
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.logger = get_logger("ObjectiveFormulator", level=config.log_level)
    
    def formulate_objectives(
        self,
        prompt: str,
        assessment: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Formulate objectives from user prompt.
        
        Args:
            prompt: The user's input prompt
            assessment: Results from Layer 1 assessment
            context: Optional context from previous interactions
            
        Returns:
            Structured objectives data
        """
        self.logger.info("Formulating objectives from user prompt")
        
        # Multi-provider objective extraction
        objective_candidates = []
        
        for provider_name in ["openai", "groq", "gemini"]:
            provider = self.provider_manager.get_provider(provider_name)
            if provider:
                try:
                    result = provider.extract_objectives(prompt)
                    parsed_result = self._parse_objectives(result, provider_name)
                    objective_candidates.append(parsed_result)
                except Exception as e:
                    self.logger.warning(f"Provider {provider_name} failed for objective extraction: {str(e)}")
                    continue
        
        # Synthesize objectives
        synthesized_objectives = self._synthesize_objectives(objective_candidates)
        
        # Critique and refine
        critiqued_objectives = self._critique_objectives(synthesized_objectives, prompt)
        
        # Generate expected outcomes and success criteria
        final_objectives = self._enhance_objectives(critiqued_objectives, prompt, context)
        
        self.logger.info(f"Formulated {len(final_objectives['primary_objectives'])} primary objectives")
        
        return final_objectives
    
    def _parse_objectives(self, raw_response: str, provider_name: str) -> Dict[str, Any]:
        """
        Parse objectives from provider response.
        
        Args:
            raw_response: Raw response from provider
            provider_name: Name of the provider
            
        Returns:
            Parsed objectives data
        """
        try:
            # Try to extract JSON from response
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = raw_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                return {
                    "primary_objectives": result.get("primary_objectives", []),
                    "secondary_objectives": result.get("secondary_objectives", []),
                    "expected_outcomes": result.get("expected_outcomes", []),
                    "constraints": result.get("constraints", []),
                    "provider": provider_name
                }
            else:
                # Fallback: create objectives from text
                return self._extract_objectives_fallback(raw_response, provider_name)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse objectives from {provider_name}: {str(e)}")
            return self._extract_objectives_fallback(raw_response, provider_name)
    
    def _extract_objectives_fallback(self, text: str, provider_name: str) -> Dict[str, Any]:
        """
        Fallback method to extract objectives from text.
        
        Args:
            text: Raw text response
            provider_name: Name of the provider
            
        Returns:
            Basic objectives structure
        """
        # Simple keyword-based extraction
        lines = text.split('\n')
        objectives = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('1.')):
                objective = line.lstrip('-*1234567890. ').strip()
                if objective:
                    objectives.append(objective)
        
        if not objectives:
            objectives = [f"Analyze and respond to: {text[:100]}..."]
        
        return {
            "primary_objectives": objectives[:3],  # Take first 3 as primary
            "secondary_objectives": objectives[3:],  # Rest as secondary
            "expected_outcomes": [],
            "constraints": [],
            "provider": provider_name
        }
    
    def _synthesize_objectives(self, objective_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize objectives from multiple providers.
        
        Args:
            objective_candidates: List of objective candidates from providers
            
        Returns:
            Synthesized objectives
        """
        if not objective_candidates:
            return {
                "primary_objectives": ["Complete the requested task"],
                "secondary_objectives": [],
                "expected_outcomes": [],
                "constraints": []
            }
        
        # Combine all objectives
        all_primary = []
        all_secondary = []
        all_outcomes = []
        all_constraints = []
        
        for candidate in objective_candidates:
            all_primary.extend(candidate.get("primary_objectives", []))
            all_secondary.extend(candidate.get("secondary_objectives", []))
            all_outcomes.extend(candidate.get("expected_outcomes", []))
            all_constraints.extend(candidate.get("constraints", []))
        
        # Deduplicate and prioritize
        unique_primary = self._deduplicate_objectives(all_primary)
        unique_secondary = self._deduplicate_objectives(all_secondary)
        unique_outcomes = self._deduplicate_objectives(all_outcomes)
        unique_constraints = self._deduplicate_objectives(all_constraints)
        
        return {
            "primary_objectives": unique_primary[:5],  # Limit to 5 primary
            "secondary_objectives": unique_secondary[:3],  # Limit to 3 secondary
            "expected_outcomes": unique_outcomes,
            "constraints": unique_constraints
        }
    
    def _deduplicate_objectives(self, objectives: List[str]) -> List[str]:
        """
        Remove duplicate and similar objectives.
        
        Args:
            objectives: List of objectives
            
        Returns:
            Deduplicated list
        """
        if not objectives:
            return []
        
        unique_objectives = []
        
        for obj in objectives:
            obj_clean = obj.lower().strip()
            
            # Check if similar objective already exists
            is_duplicate = False
            for existing in unique_objectives:
                existing_clean = existing.lower().strip()
                
                # Simple similarity check
                if (obj_clean in existing_clean or 
                    existing_clean in obj_clean or
                    self._calculate_similarity(obj_clean, existing_clean) > 0.8):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_objectives.append(obj)
        
        return unique_objectives
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate simple similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _critique_objectives(self, objectives: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """
        Critique and refine objectives for clarity and feasibility.
        
        Args:
            objectives: Initial objectives
            original_prompt: Original user prompt
            
        Returns:
            Critiqued and refined objectives
        """
        # For now, return as-is with basic validation
        refined_objectives = objectives.copy()
        
        # Ensure we have at least one primary objective
        if not refined_objectives["primary_objectives"]:
            refined_objectives["primary_objectives"] = [
                f"Address the user's request: {original_prompt[:100]}..."
            ]
        
        return refined_objectives
    
    def _enhance_objectives(
        self,
        objectives: Dict[str, Any],
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance objectives with success criteria and detailed outcomes.
        
        Args:
            objectives: Base objectives
            prompt: Original prompt
            context: Optional context
            
        Returns:
            Enhanced objectives with success criteria
        """
        enhanced = objectives.copy()
        
        # Generate success criteria
        enhanced["success_criteria"] = []
        for obj in enhanced["primary_objectives"]:
            criteria = f"Successfully complete: {obj}"
            enhanced["success_criteria"].append(criteria)
        
        # Generate expected outcomes if not present
        if not enhanced["expected_outcomes"]:
            enhanced["expected_outcomes"] = [
                {
                    "outcome": f"Completion of {obj}",
                    "measurable_criteria": f"Objective '{obj}' is fully addressed",
                    "timeline": "Within execution timeframe"
                }
                for obj in enhanced["primary_objectives"]
            ]
        
        return enhanced
