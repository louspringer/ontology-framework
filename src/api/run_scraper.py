"""
Script to run the documentation scraper.
"""

import logging
import sys
from typing import List, Dict, Any, Optional, cast
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from src.api.documentation_scraper import DocumentationScraper

def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('documentation_scraping.log')
        ]
    )

def get_ip_address() -> str:
    """Get the public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return f"Failed to get IP: {str(e)}"

def analyze_html_response(content: str) -> Dict[str, List[str]]:
    """Analyze HTML response for API-related content."""
    soup = BeautifulSoup(content, 'html.parser')
    
    analysis: Dict[str, List[str]] = {
        'api_references': [],
        'api_endpoints': [],
        'auth_methods': [],
        'ui_strings': []
    }
    
    # Look for API-related text
    api_patterns = [
        'API key',
        'Bearer token',
        'Authentication',
        'Endpoints',
        'Documentation',
        '/api/',
        'swagger',
        'openapi'
    ]
    
    for pattern in api_patterns:
        elements = soup.find_all(string=lambda text: isinstance(text, (str, NavigableString)) and pattern.lower() in text.lower())
        if elements:
            analysis['api_references'].extend(str(e).strip() for e in elements)
    
    # Look for script tags that might contain API info
    scripts = soup.find_all('script')
    for script in scripts:
        if isinstance(script, Tag) and script.string and 'api' in script.string.lower():
            analysis['ui_strings'].append(str(script.string))
    
    return analysis

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Log IP address
    ip_address = get_ip_address()
    logger.info(f"Running scraper from IP: {ip_address}")
    
    # Common API documentation endpoints to try
    endpoints = [
        '/api/alpha/docs',
        '/api/alpha/swagger',
        '/api/alpha/openapi.json',
        '/api/alpha/api-docs',
        '/api/alpha/documentation',
        '/api/alpha/metamodel',
        '/api/alpha/schema',
        '/api/alpha/model',
        '/api/alpha/ontology'
    ]
    
    scraper = DocumentationScraper('https://app.boldo.io')
    findings: Dict[str, Any] = {}
    max_failures = 3
    failure_count = 0
    
    for endpoint in endpoints:
        try:
            logger.info(f"Attempting to scrape documentation from endpoint: {endpoint}")
            content = scraper.scrape_documentation(endpoint)
            
            if content:
                # Analyze the content
                analysis = scraper.analyze_content(content)
                
                if analysis['api_endpoints'] or analysis['metamodel']['entities']:
                    findings[endpoint] = analysis
                    logger.info(f"Found API/metamodel information at {endpoint}")
                    logger.info(f"API Endpoints: {analysis['api_endpoints']}")
                    logger.info(f"Metamodel Entities: {analysis['metamodel']['entities']}")
                    
                    # Save the findings
                    scraper.save_analysis(analysis, f'api_documentation_{endpoint.replace("/", "_")}.json')
                    scraper.save_ontology(f'documentation_ontology_{endpoint.replace("/", "_")}.ttl')
                    
                else:
                    logger.warning(f"No relevant information found at {endpoint}")
                    failure_count += 1
            else:
                logger.warning(f"Failed to get content from {endpoint}")
                failure_count += 1
                
            if failure_count >= max_failures:
                logger.error(f"Maximum number of failures ({max_failures}) reached. Exiting.")
                break
                
        except Exception as e:
            logger.error(f"Error processing {endpoint}: {str(e)}")
            failure_count += 1
            if failure_count >= max_failures:
                logger.error(f"Maximum number of failures ({max_failures}) reached. Exiting.")
                break
    
    if not findings:
        logger.error("Failed to find any API documentation")
        sys.exit(1)
    else:
        # Save overall findings
        with open('api_documentation_findings.json', 'w') as f:
            json.dump(findings, f, indent=2)
        logger.info("Saved findings to api_documentation_findings.json")

if __name__ == '__main__':
    main() 