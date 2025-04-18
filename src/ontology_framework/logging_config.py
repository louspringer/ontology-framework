import logging
import logging.handlers
from pathlib import Path
from typing import Optional

class OntologyFrameworkLogger:
    """Logging configuration following guidance.ttl standards."""
    
    @classmethod
    def get_logger(cls, name: str, log_dir: Optional[str] = None) -> 'OntologyFrameworkLogger':
        """Get a logger instance for the given name.
        
        Args:
            name: The name of the logger
            log_dir: Optional directory for log files
            
        Returns:
            An OntologyFrameworkLogger instance
        """
        return cls(name, log_dir)
    
    def __init__(self, name: str, log_dir: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters with default values for context and traceback
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'Context: %(context)s\n'
            'Traceback: %(traceback)s',
            defaults={'context': '{}', 'traceback': ''}
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            defaults={'context': '{}', 'traceback': ''}
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if log_dir provided
        if log_dir:
            log_path = Path(log_dir) / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, context: Optional[dict] = None, traceback: Optional[str] = None):
        self.logger.debug(msg, extra={'context': context or {}, 'traceback': traceback or ''})
    
    def info(self, msg: str, context: Optional[dict] = None):
        self.logger.info(msg, extra={'context': context or {}, 'traceback': ''})
    
    def warning(self, msg: str, context: Optional[dict] = None):
        self.logger.warning(msg, extra={'context': context or {}, 'traceback': ''})
    
    def error(self, msg: str, context: Optional[dict] = None, traceback: Optional[str] = None):
        self.logger.error(msg, extra={'context': context or {}, 'traceback': traceback or ''})
    
    def critical(self, msg: str, context: Optional[dict] = None, traceback: Optional[str] = None):
        self.logger.critical(msg, extra={'context': context or {}, 'traceback': traceback or ''})

# Global logger instance
framework_logger = OntologyFrameworkLogger('ontology_framework', 'logs') 