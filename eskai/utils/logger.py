"""
Comprehensive logging system for ESKAI
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ESKAIFormatter(logging.Formatter):
    """
    Custom formatter for ESKAI logs with structured output.
    """
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        execution_id = getattr(record, 'execution_id', None)
        if execution_id is not None:
            log_entry['execution_id'] = execution_id
        layer = getattr(record, 'layer', None)
        if layer is not None:
            log_entry['layer'] = layer
        agent_id = getattr(record, 'agent_id', None)
        if agent_id is not None:
            log_entry['agent_id'] = agent_id
        tool_name = getattr(record, 'tool_name', None)
        if tool_name is not None:
            log_entry['tool_name'] = tool_name
        
        return json.dumps(log_entry, indent=None)


class ESKAILogger:
    """
    Enhanced logger for ESKAI with context tracking.
    """
    
    def __init__(self, name: str, level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(ESKAIFormatter())
            self.logger.addHandler(file_handler)
        
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context for subsequent log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear the current context."""
        self.context = {}
    
    def _log_with_context(self, level, message, **kwargs):
        """Log message with current context."""
        extra = {**self.context, **kwargs}
        getattr(self.logger, level)(message, extra=extra)
    
    def debug(self, message, **kwargs):
        """Log debug message."""
        self._log_with_context('debug', message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log info message."""
        self._log_with_context('info', message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message."""
        self._log_with_context('warning', message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log error message."""
        self._log_with_context('error', message, **kwargs)
    
    def critical(self, message, **kwargs):
        """Log critical message."""
        self._log_with_context('critical', message, **kwargs)


# Global logger cache
_loggers: Dict[str, ESKAILogger] = {}


def get_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> ESKAILogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        ESKAILogger instance
    """
    logger_key = f"{name}_{level}_{log_file}"
    
    if logger_key not in _loggers:
        _loggers[logger_key] = ESKAILogger(name, level, log_file)
    
    return _loggers[logger_key]


class ExecutionTracker:
    """
    Track execution metrics and performance.
    """
    
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.start_time = time.time()
        self.events = []
        self.metrics = {}
    
    def log_event(self, event_type: str, description: str, **kwargs):
        """Log an execution event."""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "description": description,
            "data": kwargs
        }
        self.events.append(event)
    
    def set_metric(self, name: str, value: Any):
        """Set a performance metric."""
        self.metrics[name] = value
    
    def get_duration(self) -> float:
        """Get total execution duration."""
        return time.time() - self.start_time
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "execution_id": self.execution_id,
            "duration": self.get_duration(),
            "events_count": len(self.events),
            "metrics": self.metrics,
            "events": self.events
        }
