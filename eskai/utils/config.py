"""
Configuration management for ESKAI
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ESKAIConfig:
    """
    Configuration class for ESKAI framework.
    """
    
    # API Keys
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    
    # Provider Settings
    openai_model: str = "gpt-4"
    groq_model: str = "mixtral-8x7b-32768"
    gemini_model: str = "gemini-pro"
    temperature: float = 0.7
    
    # Execution Settings
    max_concurrent_agents: int = 3
    enable_parallel_execution: bool = True
    default_timeout: int = 3600  # 1 hour in seconds
    
    # Tool Settings
    enable_internet: bool = True
    enable_code_execution: bool = True
    enable_file_operations: bool = True
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = "eskai.log"
    
    # Safety Settings
    max_tool_execution_time: int = 300  # 5 minutes
    sandbox_code_execution: bool = True
    max_file_size_mb: int = 100
    
    # Advanced Settings
    retry_attempts: int = 3
    retry_delay: float = 1.0
    cache_responses: bool = True
    
    @classmethod
    def from_file(cls, config_path: str) -> "ESKAIConfig":
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            ESKAIConfig instance
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Extract ESKAI-specific configuration
        eskai_config = config_data.get('eskai', {})
        
        # Flatten nested configuration
        flat_config = {}
        
        # Provider settings
        providers = eskai_config.get('providers', {})
        if 'openai' in providers:
            flat_config.update({
                'openai_model': providers['openai'].get('model', 'gpt-4'),
                'temperature': providers['openai'].get('temperature', 0.7)
            })
        if 'groq' in providers:
            flat_config['groq_model'] = providers['groq'].get('model', 'mixtral-8x7b-32768')
        if 'gemini' in providers:
            flat_config['gemini_model'] = providers['gemini'].get('model', 'gemini-pro')
        
        # Execution settings
        execution = eskai_config.get('execution', {})
        flat_config.update({
            'max_concurrent_agents': execution.get('max_concurrent_agents', 3),
            'default_timeout': execution.get('timeout_seconds', 3600),
            'enable_parallel_execution': execution.get('enable_parallel_execution', True)
        })
        
        # Tool settings
        tools = eskai_config.get('tools', {})
        flat_config.update({
            'enable_internet': tools.get('enable_internet', True),
            'enable_code_execution': tools.get('enable_code_execution', True),
            'enable_file_operations': tools.get('enable_file_operations', True)
        })
        
        # Logging settings
        logging = eskai_config.get('logging', {})
        flat_config.update({
            'log_level': logging.get('level', 'INFO'),
            'log_file': logging.get('file', 'eskai.log')
        })
        
        return cls(**flat_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            'openai_api_key': self.openai_api_key,
            'groq_api_key': self.groq_api_key,
            'gemini_api_key': self.gemini_api_key,
            'openai_model': self.openai_model,
            'groq_model': self.groq_model,
            'gemini_model': self.gemini_model,
            'temperature': self.temperature,
            'max_concurrent_agents': self.max_concurrent_agents,
            'enable_parallel_execution': self.enable_parallel_execution,
            'default_timeout': self.default_timeout,
            'enable_internet': self.enable_internet,
            'enable_code_execution': self.enable_code_execution,
            'enable_file_operations': self.enable_file_operations,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'max_tool_execution_time': self.max_tool_execution_time,
            'sandbox_code_execution': self.sandbox_code_execution,
            'max_file_size_mb': self.max_file_size_mb,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay,
            'cache_responses': self.cache_responses
        }
    
    def validate(self) -> None:
        """
        Validate the configuration settings.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.openai_api_key and not self.groq_api_key and not self.gemini_api_key:
            raise ValueError("At least one API key must be provided")
        
        if self.max_concurrent_agents < 1:
            raise ValueError("max_concurrent_agents must be at least 1")
        
        if self.default_timeout < 60:
            raise ValueError("default_timeout must be at least 60 seconds")
        
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")


def get_default_config() -> ESKAIConfig:
    """
    Get the default ESKAI configuration.
    
    Returns:
        Default ESKAIConfig instance
    """
    return ESKAIConfig()
