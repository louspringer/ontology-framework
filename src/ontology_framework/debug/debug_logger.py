# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import logging
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import threading
from contextlib import contextmanager
import sys
import traceback
import os
import socket
from dataclasses import dataclass, asdict
from enum import Enum
import time

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log level enumeration."""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@dataclass
class LogContext:
    """Context for a log entry."""
    timestamp: str
    level: LogLevel
    module: str
    function: str
    line: int
    message: str
    context: Dict[str, Any]
    trace: Optional[str] = None
    duration: Optional[float] = None

class DebugLogger:
    """Enhanced debug logger with context tracking and performance monitoring."""
    
    def __init__(
        self,
        enabled: bool = False,
        min_level: LogLevel = LogLevel.DEBUG,
        log_dir: Optional[Path] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        max_files: int = 5
    ):
        """Initialize the debug logger.
        
        Args:
            enabled: Whether the logger is enabled
            min_level: Minimum log level to record
            log_dir: Optional log directory path
            max_file_size: Maximum size per log file in bytes
            max_files: Maximum number of log files to keep
        """
        self.enabled = enabled
        self.min_level = min_level
        self.log_dir = log_dir or Path("logs/debug")
        self.max_file_size = max_file_size
        self.max_files = max_files
        
        self.context_stack: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._setup_logging()
        
        # Track performance metrics
        self.start_time = time.time()
        self.operation_times: Dict[str, List[float]] = {}
    
    def _setup_logging(self):
        """Setup debug logging."""
        if not self.enabled:
            return
            
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create base log file
        self.current_log_file = self.log_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure file handler
        file_handler = logging.FileHandler(self.current_log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        
        # Log initial system info
        self._log_system_info()
    
    def _log_system_info(self):
        """Log system information."""
        if not self.enabled:
            return
            
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'hostname': socket.gethostname(),
            'python_version': sys.version,
            'platform': sys.platform,
            'environment': {
                k: v for k, v in os.environ.items()
                if 'SECRET' not in k.upper()
                and 'PASSWORD' not in k.upper()
                and 'TOKEN' not in k.upper()
            }
        }
        
        self.log(
            LogLevel.INFO,
            "System Information",
            context=system_info
        )
    
    def _rotate_logs(self):
        """Rotate log files if current file exceeds size limit."""
        if not self.enabled:
            return
            
        try:
            if self.current_log_file.stat().st_size > self.max_file_size:
                # Rotate existing files
                for i in range(self.max_files - 1, 0, -1):
                    old_file = self.log_dir / f"debug_{i}.log"
                    new_file = self.log_dir / f"debug_{i + 1}.log"
                    if old_file.exists():
                        if i == self.max_files - 1:
                            old_file.unlink()
                        else:
                            old_file.rename(new_file)
                
                # Rename current file
                self.current_log_file.rename(self.log_dir / "debug_1.log")
                
                # Create new log file
                self.current_log_file = self.log_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                
                # Update file handler
                for handler in logger.handlers[:]:
                    if isinstance(handler, logging.FileHandler):
                        logger.removeHandler(handler)
                
                file_handler = logging.FileHandler(self.current_log_file)
                file_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                )
                logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to rotate log files: {e}")
    
    def _get_caller_info(self) -> Dict[str, Any]:
        """Get information about the calling function."""
        frame = sys._getframe(2)  # Skip this function and log function
        return {
            'module': frame.f_globals.get('__name__', 'unknown'),
            'function': frame.f_code.co_name,
            'line': frame.f_lineno
        }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for logging."""
        try:
            return json.dumps(context, indent=2)
        except Exception:
            return str(context)
    
    def log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        trace: bool = False
    ):
        """Log a message with context.
        
        Args:
            level: Log level
            message: Log message
            context: Optional context dictionary
            trace: Whether to include stack trace
        """
        if not self.enabled or level.value < self.min_level.value:
            return
            
        with self._lock:
            # Check log rotation
            self._rotate_logs()
            
            # Get caller info
            caller_info = self._get_caller_info()
            
            # Build context
            full_context = {}
            for ctx in self.context_stack:
                full_context.update(ctx)
            if context:
                full_context.update(context)
            
            # Create log entry
            entry = LogContext(
                timestamp=datetime.now().isoformat(),
                level=level,
                module=caller_info['module'],
                function=caller_info['function'],
                line=caller_info['line'],
                message=message,
                context=full_context,
                trace=traceback.format_stack() if trace else None
            )
            
            # Log the entry
            log_message = (
                f"[{entry.module}.{entry.function}:{entry.line}] {message}\n"
                f"Context: {self._format_context(full_context)}"
            )
            if trace:
                log_message += f"\nTrace:\n{''.join(entry.trace)}"
            
            logger.log(level.value, log_message)
    
    def trace(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a trace message."""
        self.log(LogLevel.TRACE, message, context)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        self.log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        self.log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log an error message with trace."""
        self.log(LogLevel.ERROR, message, context, trace=True)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a critical message with trace."""
        self.log(LogLevel.CRITICAL, message, context, trace=True)
    
    @contextmanager
    def context(self, **kwargs):
        """Context manager for adding context to logs.
        
        Args:
            **kwargs: Context key-value pairs
        """
        if not self.enabled:
            yield
            return
            
        self.context_stack.append(kwargs)
        try:
            yield
        finally:
            self.context_stack.pop()
    
    @contextmanager
    def operation(self, name: str, context: Optional[Dict[str, Any]] = None):
        """Context manager for tracking operation timing.
        
        Args:
            name: Operation name
            context: Optional operation context
        """
        if not self.enabled:
            yield
            return
            
        start_time = time.time()
        
        try:
            with self.context(operation=name, **context or {}):
                self.debug(f"Starting operation: {name}")
                yield
        finally:
            duration = time.time() - start_time
            
            if name not in self.operation_times:
                self.operation_times[name] = []
            self.operation_times[name].append(duration)
            
            self.debug(
                f"Completed operation: {name}",
                {'duration': duration}
            )
    
    def get_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for operations.
        
        Returns:
            Dict[str, Dict[str, float]]: Operation timing metrics
        """
        if not self.enabled:
            return {}
            
        metrics = {}
        for op_name, times in self.operation_times.items():
            if times:
                metrics[op_name] = {
                    'count': len(times),
                    'total_time': sum(times),
                    'average_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times)
                }
        return metrics
    
    def export_metrics(self, export_path: Optional[Path] = None) -> None:
        """Export performance metrics to file.
        
        Args:
            export_path: Optional path to export to
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_path is None:
                export_path = self.log_dir / f"metrics_{timestamp}.json"
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_runtime': time.time() - self.start_time,
                'operations': self.get_performance_metrics()
            }
            
            export_path.write_text(json.dumps(metrics, indent=2))
            logger.info(f"Performance metrics exported to {export_path}") 