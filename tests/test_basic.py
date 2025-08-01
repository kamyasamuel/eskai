"""
Basic tests for ESKAI framework
"""

import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import eskai
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eskai import ESKAI, ESKAIConfig

class TestESKAI:
    """Test cases for main ESKAI class"""
    
    def test_eskai_initialization(self):
        """Test ESKAI can be initialized with default config"""
        config = ESKAIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"), # type: ignore
            groq_api_key=os.getenv("GROQ_API_KEY"), # type: ignore
            gemini_api_key=os.getenv("GEMINI_API_KEY") # type: ignore
        )
        
        with patch('eskai.providers.openai_client.OpenAI'):
            agi = ESKAI(config=config)
            assert agi is not None
            assert agi.config == config
    
    def test_chat_response(self):
        """Test simple chat response"""
        config = ESKAIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"), # type: ignore
            groq_api_key=os.getenv("GROQ_API_KEY"), # type: ignore
            gemini_api_key=os.getenv("GEMINI_API_KEY") # type: ignore
        )
        
        with patch('eskai.providers.openai_client.OpenAI') as mock_openai:
            # Mock the provider response chain properly
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Create a mock response object
            mock_response = Mock()
            mock_message = Mock()
            mock_choice = Mock()
            
            mock_message.content = "Hello! How can I help you?"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            agi = ESKAI(config=config)
            
            # Mock the layer 1 assessment to return chat intent
            with patch.object(agi.layer1, 'assess_intent') as mock_assess:
                mock_assess.return_value = {
                    "intent": "chat",
                    "confidence": 0.9,
                    "reasoning": "Simple greeting"
                }
                
                result = agi.process("Hello")
                
                assert result["type"] == "chat"
                assert "response" in result


class TestConfig:
    """Test cases for configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ESKAIConfig()
        assert config.max_concurrent_agents == 3
        assert config.enable_parallel_execution is True
        assert config.log_level == "INFO"
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ESKAIConfig()
        
        # Should not raise with valid config
        config.validate()
        
        # Should raise with invalid config
        config.max_concurrent_agents = 0
        with pytest.raises(ValueError):
            config.validate()


if __name__ == "__main__":
    pytest.main([__file__])
