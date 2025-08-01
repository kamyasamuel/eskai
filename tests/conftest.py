"""
Test configuration and fixtures
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch
from eskai import ESKAIConfig

# Add the parent directory to the path so we can import eskai
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def test_config():
    """Provide a test configuration"""
    return ESKAIConfig(
        openai_api_key="test-openai-key",
        groq_api_key="test-groq-key", 
        gemini_api_key="test-gemini-key",
        log_level="DEBUG",
        max_concurrent_agents=2,
        default_timeout=300
    )


@pytest.fixture
def mock_providers():
    """Mock all AI providers"""
    with patch('eskai.providers.openai_client.OpenAI'), \
         patch('eskai.providers.groq_client.GroqClient'), \
         patch('eskai.providers.gemini_client.GeminiClient'):
        yield


# Test data
SAMPLE_PROMPTS = {
    "chat": [
        "Hello",
        "Hi there",
        "How are you?",
        "Good morning",
        "Thanks"
    ],
    "objective": [
        "Create a market analysis for electric vehicles",
        "Build a Python web scraper for job listings",
        "Analyze the latest AI trends and write a report",
        "Develop a business plan for a tech startup",
        "Research and summarize climate change impacts"
    ]
}
