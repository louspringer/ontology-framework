import os
import json
import logging
from ontology_framework.config.logging_config import setup_logging, get_logger
from ontology_framework.config.correlation import CorrelationManager

def test_structured_logging():
    # Set up logging with JSON format
    log_file = 'logs/test_structured.log'
    # Clear the log file before running the test
    open(log_file, 'w').close()
    setup_logging(log_file, log_format='json')
    logger = get_logger('test_structured')

    # Log a message with correlation ID and metadata
    with CorrelationManager() as mgr:
        logger.info('Test structured log message', extra={'metadata': {'key': 'value'}})
        expected_correlation_id = mgr.get_current_context().correlation_id

    # Read the log file and find the correct log entry
    found = False
    with open(log_file, 'r') as f:
        for line in f:
            log_record = json.loads(line.strip())
            if log_record.get('logger') == 'test_structured':
                assert log_record['level'] == 'INFO'
                assert log_record['logger'] == 'test_structured'
                assert log_record['message'] == 'Test structured log message'
                print('Expected correlation_id:', expected_correlation_id)
                print('Log record correlation_id:', log_record['correlation_id'])
                assert log_record['correlation_id'] == expected_correlation_id
                assert log_record['metadata'] == {'key': 'value'}
                found = True
                break
    assert found, "Structured log entry for 'test_structured' not found."
    print('Structured logging test passed!')

if __name__ == '__main__':
    test_structured_logging() 