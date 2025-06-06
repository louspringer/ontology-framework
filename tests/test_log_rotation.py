import os
import logging
from ontology_framework.config.logging_config import setup_logging, get_logger

def test_log_rotation():
    # Set up logging with a small max_bytes value to trigger rotation
    log_file = 'logs/test_rotation.log'
    max_bytes = 1024  # 1KB
    backup_count = 3
    setup_logging(log_file, log_format='plain', max_bytes=max_bytes, backup_count=backup_count)
    logger = get_logger('test_rotation')

    # Log a large number of messages to trigger rotation
    for i in range(1000):
        logger.info(f'Test log message {i}')

    # Check that log rotation occurred
    log_files = [f for f in os.listdir('logs') if f.startswith('test_rotation.log')]
    assert len(log_files) > 1, "Log rotation did not occur."
    print('Log rotation test passed!')

if __name__ == '__main__':
    test_log_rotation() 