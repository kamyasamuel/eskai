"""
Provider Manager for handling multiple AI providers
"""

from typing import Dict, Any, Optional, List
from ..utils.logger import get_logger
from .openai_client import OpenAIClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient


class ProviderManager:
    """
    Manages multiple AI providers and handles failover.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("ProviderManager", level=config.log_level)
        self.providers = {}
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        
        # OpenAI
        if self.config.openai_api_key:
            try:
                self.providers["openai"] = OpenAIClient(
                    api_key=self.config.openai_api_key,
                    model=self.config.openai_model,
                    temperature=self.config.temperature
                )
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI provider: {str(e)}")
        
        # Groq
        if self.config.groq_api_key:
            try:
                self.providers["groq"] = GroqClient(
                    api_key=self.config.groq_api_key,
                    model=self.config.groq_model,
                    temperature=self.config.temperature
                )
                self.logger.info("Groq provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Groq provider: {str(e)}")
        
        # Gemini
        if self.config.gemini_api_key:
            try:
                self.providers["gemini"] = GeminiClient(
                    api_key=self.config.gemini_api_key,
                    model=self.config.gemini_model,
                    temperature=self.config.temperature
                )
                self.logger.info("Gemini provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini provider: {str(e)}")
        
        if not self.providers:
            raise RuntimeError("No AI providers could be initialized. Please check your API keys.")
        
        self.logger.info(f"Initialized {len(self.providers)} providers: {list(self.providers.keys())}")
    
    def get_provider(self, provider_name: str) -> Optional[Any]:
        """
        Get a specific provider by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider instance or None if not available
        """
        return self.providers.get(provider_name)
    
    def get_primary_provider(self) -> Any:
        """
        Get the primary provider (first available).
        
        Returns:
            Primary provider instance
        """
        if "openai" in self.providers:
            return self.providers["openai"]
        elif "groq" in self.providers:
            return self.providers["groq"]
        elif "gemini" in self.providers:
            return self.providers["gemini"]
        else:
            raise RuntimeError("No providers available")
    
    def get_all_providers(self) -> List[Any]:
        """
        Get all available providers.
        
        Returns:
            List of provider instances
        """
        return list(self.providers.values())
    
    def generate_with_failover(self, prompt: str, **kwargs) -> str:
        """
        Generate response with automatic failover between providers.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response
        """
        last_error = None
        
        for provider_name, provider in self.providers.items():
            try:
                self.logger.debug(f"Attempting generation with {provider_name}")
                response = provider.generate_response(prompt, **kwargs)
                self.logger.debug(f"Successful generation with {provider_name}")
                return response
            except Exception as e:
                last_error = e
                self.logger.warning(f"Provider {provider_name} failed: {str(e)}")
                continue
        
        # If all providers failed
        raise RuntimeError(f"All providers failed. Last error: {str(last_error)}")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get status of all providers.
        
        Returns:
            Dictionary with provider status information
        """
        status = {}
        
        for name, provider in self.providers.items():
            try:
                # Try a simple test to check if provider is working
                test_response = provider.generate_response("Test", max_tokens=1)
                status[name] = {
                    "available": True,
                    "model": getattr(provider, 'model', 'unknown'),
                    "last_test": "success"
                }
            except Exception as e:
                status[name] = {
                    "available": False,
                    "error": str(e),
                    "last_test": "failed"
                }
        
        return status
