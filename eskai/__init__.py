"""
ESKAI - Evolved Strategic Knowledge and AI Framework

A sophisticated multi-layered AGI framework for complex problem-solving.
"""

__version__ = "0.1.1"
__author__ = "ESKAI Team"
__email__ = "kamyasamuel@eskaen.com"
__license__ = "MIT"

from .core.eskai_main import ESKAI
from .utils.config import ESKAIConfig
from .utils.logger import get_logger

__all__ = ["ESKAI", "ESKAIConfig", "get_logger"]
