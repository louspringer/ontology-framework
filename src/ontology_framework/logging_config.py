import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

class OntologyFrameworkLogger:
    """Centralized logging configuration for the Ontology Framework."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = "ontology_framework", log_dir: Optional[str] = None):
        if not OntologyFrameworkLogger._initialized:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)
            
            # Clear any existing handlers
            self.logger.handlers.clear()
            
            # Detailed formatter for file logging
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            
            # Simple formatter for console output
            simple_formatter = logging.Formatter(
                '%(levelname)s - %(message)s'
            )
            
            # Console handler (INFO level)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            # File handler (DEBUG level) if log directory is provided
            if log_dir:
                log_path = Path(log_dir)
                log_path.mkdir(parents=True, exist_ok=True)
                file_handler = logging.handlers.RotatingFileHandler(
                    log_path / "ontology_framework.log",
                    maxBytes=10485760,  # 10MB
                    backupCount=5
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(file_handler)
            
            OntologyFrameworkLogger._initialized = True
    
    @classmethod
    def get_logger(cls, name: str = "ontology_framework", log_dir: Optional[str] = None) -> logging.Logger:
        """Get or create a logger instance.
        
        Args:
            name: The name for the logger
            log_dir: Optional directory for log files
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if not cls._initialized:
            cls(name, log_dir)
        return cls._instance.logger
    
    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)

# Global logger instance
framework_logger = OntologyFrameworkLogger('ontology_framework', 'logs') 