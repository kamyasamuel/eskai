"""
Layer 1: Prompt Assessment
Determines user intent and classifies prompts as chat or objective-driven.
"""

import re
from typing import Dict, Any, Optional, List
from ..utils.logger import get_logger


class PromptAssessor:
    """
    Assesses user prompts to determine intent and processing requirements.
    """
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.logger = get_logger("PromptAssessor", level=config.log_level)
        
        # Predefined patterns for quick classification
        self.chat_patterns = [
            r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|what\'s up|how\'s it going)\b',
            r'\b(thanks|thank you|bye|goodbye|see you)\b',
            r'\b(nice|great|awesome|cool|interesting)\b$',
            r'^\s*(yes|no|ok|okay|sure|alright)\s*$'
        ]
        
        self.objective_patterns = [
            r'\b(create|build|make|develop|design|implement)\b',
            r'\b(analyze|research|investigate|study|examine)\b',
            r'\b(solve|fix|resolve|address|handle)\b',
            r'\b(generate|produce|write|compose|draft)\b',
            r'\b(plan|strategy|approach|method|solution)\b',
            r'\b(help me|can you|please|I need)\b.*\b(with|to|for)\b'
        ]
    
    def assess_intent(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess the intent of a user prompt.
        
        Args:
            prompt: The user's input prompt
            context: Optional context from previous interactions
            
        Returns:
            Dictionary containing intent classification and metadata
        """
        self.logger.info("Assessing prompt intent")
        
        # Quick pattern matching first
        quick_assessment = self._quick_pattern_match(prompt)
        
        if quick_assessment["confidence"] > 0.8:
            self.logger.info(f"High confidence quick assessment: {quick_assessment['intent']}")
            return quick_assessment
        
        # Multi-provider assessment for uncertain cases
        self.logger.info("Running multi-provider intent assessment")
        provider_results = self._multi_provider_assessment(prompt, context)
        
        # Consensus decision
        final_assessment = self._consensus_decision(provider_results, quick_assessment)
        
        self.logger.info(f"Final intent assessment: {final_assessment['intent']} (confidence: {final_assessment['confidence']:.2f})")
        
        return final_assessment
    
    def _quick_pattern_match(self, prompt: str) -> Dict[str, Any]:
        """
        Quick pattern-based classification.
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            Quick assessment result
        """
        prompt_lower = prompt.lower().strip()
        
        # Check for chat patterns
        chat_score = 0
        for pattern in self.chat_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                chat_score += 1
        
        # Check for objective patterns
        objective_score = 0
        for pattern in self.objective_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                objective_score += 1
        
        # Length and complexity heuristics
        word_count = len(prompt.split())
        has_question_mark = '?' in prompt
        has_complex_structure = len(prompt.split('.')) > 2 or len(prompt.split(',')) > 3
        
        # Adjust scores based on heuristics
        if word_count > 20 or has_complex_structure:
            objective_score += 1
        
        if word_count < 5 and not has_question_mark:
            chat_score += 1
        
        # Determine intent and confidence
        total_score = chat_score + objective_score
        
        if total_score == 0:
            # Ambiguous case
            intent = "objective"  # Default to objective for safety
            confidence = 0.3
        elif chat_score > objective_score:
            intent = "chat"
            confidence = min(0.9, 0.5 + (chat_score - objective_score) * 0.2)
        else:
            intent = "objective"
            confidence = min(0.9, 0.5 + (objective_score - chat_score) * 0.2)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reasoning": f"Pattern matching - chat: {chat_score}, objective: {objective_score}",
            "method": "quick_pattern"
        }
    
    def _multi_provider_assessment(self, prompt: str, context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get intent assessment from multiple AI providers.
        
        Args:
            prompt: The user's input prompt
            context: Optional context from previous interactions
            
        Returns:
            List of provider assessment results
        """
        assessment_prompt = self._build_assessment_prompt(prompt, context)
        provider_results = []
        
        for provider_name in ["openai", "groq", "gemini"]:
            try:
                provider = self.provider_manager.get_provider(provider_name)
                if provider:
                    result = provider.generate_response(
                        assessment_prompt,
                        temperature=0.1  # Low temperature for consistent classification
                    )
                    
                    parsed_result = self._parse_provider_response(result, provider_name)
                    provider_results.append(parsed_result)
                    
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed for intent assessment: {str(e)}")
                continue
        
        return provider_results
    
    def _build_assessment_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Build the prompt for provider-based intent assessment.
        
        Args:
            prompt: The user's input prompt
            context: Optional context from previous interactions
            
        Returns:
            Assessment prompt for AI providers
        """
        context_info = ""
        if context:
            context_info = f"\nPrevious context: {context.get('summary', 'None')}"
        
        assessment_prompt = f"""
        Analyze the following user input and determine the intent. Classify it as either "chat" or "objective".

        User Input: "{prompt}"
        {context_info}

        Classification Criteria:
        - "chat": Casual conversation, greetings, simple questions, social pleasantries
        - "objective": Task requests, problem-solving, creation tasks, analysis requests, complex queries

        Respond in the following JSON format:
        {{
            "intent": "chat" or "objective",
            "confidence": 0.0 to 1.0,
            "reasoning": "brief explanation of the classification"
        }}
        """
        
        return assessment_prompt
    
    def _parse_provider_response(self, response: str, provider_name: str) -> Dict[str, Any]:
        """
        Parse provider response for intent assessment.
        
        Args:
            response: Raw response from provider
            provider_name: Name of the provider
            
        Returns:
            Parsed assessment result
        """
        try:
            # Try to extract JSON from response
            import json
            
            # Look for JSON content
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                return {
                    "intent": result.get("intent", "objective"),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reasoning": result.get("reasoning", "Provider assessment"),
                    "provider": provider_name
                }
            else:
                # Fallback parsing
                response_lower = response.lower()
                if "chat" in response_lower and "objective" not in response_lower:
                    intent = "chat"
                    confidence = 0.6
                else:
                    intent = "objective"
                    confidence = 0.6
                
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "reasoning": "Fallback parsing",
                    "provider": provider_name
                }
                
        except Exception as e:
            self.logger.warning(f"Failed to parse response from {provider_name}: {str(e)}")
            return {
                "intent": "objective",  # Safe default
                "confidence": 0.3,
                "reasoning": "Parsing failed",
                "provider": provider_name
            }
    
    def _consensus_decision(self, provider_results: List[Dict[str, Any]], quick_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make consensus decision from multiple assessments.
        
        Args:
            provider_results: Results from AI providers
            quick_assessment: Quick pattern-matching result
            
        Returns:
            Final consensus assessment
        """
        all_results = provider_results + [quick_assessment]
        
        # Count votes
        chat_votes = sum(1 for r in all_results if r["intent"] == "chat")
        objective_votes = sum(1 for r in all_results if r["intent"] == "objective")
        
        # Calculate weighted confidence
        chat_confidence = sum(r["confidence"] for r in all_results if r["intent"] == "chat")
        objective_confidence = sum(r["confidence"] for r in all_results if r["intent"] == "objective")
        
        if chat_votes > objective_votes:
            intent = "chat"
            confidence = min(0.95, chat_confidence / len(all_results))
        elif objective_votes > chat_votes:
            intent = "objective"
            confidence = min(0.95, objective_confidence / len(all_results))
        else:
            # Tie - use confidence scores
            if chat_confidence > objective_confidence:
                intent = "chat"
                confidence = min(0.8, chat_confidence / len(all_results))
            else:
                intent = "objective"
                confidence = min(0.8, objective_confidence / len(all_results))
        
        # Compile reasoning
        provider_intents = [f"{r.get('provider', 'pattern')}: {r['intent']}" for r in all_results]
        reasoning = f"Consensus from {len(all_results)} assessments: {', '.join(provider_intents)}"
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reasoning": reasoning,
            "method": "consensus",
            "provider_results": provider_results,
            "quick_assessment": quick_assessment
        }
