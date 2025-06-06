#!/usr/bin/env python3
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
import json
from .correlation import CorrelationFilter, get_correlation_id

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', '-'),
        }
        # Optionally include extra metadata if present
        if hasattr(record, 'metadata') and record.metadata:
            log_record['metadata'] = record.metadata
        return json.dumps(log_record)

def setup_logging(log_file: str = 'app.log', log_format: str = 'plain', max_bytes: int = 5*1024*1024, backup_count: int = 3):
    """
    Set up logging configuration for the application.
    Supports plain text and JSON log formats, with correlation ID tracking and log rotation.
    """
    log_dir = os.path.abspath(os.path.dirname(log_file))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, os.path.basename(log_file))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Choose formatter
    if log_format == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
        )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationFilter())
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(CorrelationFilter())
    root_logger.addHandler(file_handler)

    root_logger.info(f"Logging configured successfully. Log directory: {os.path.abspath(log_dir)}")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 