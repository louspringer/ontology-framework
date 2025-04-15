#!/usr/bin/env python3
"""
Script to run the API documentation scraper.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from documentation_scraper import DocumentationScraper

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for running the scraper."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('BOLDO_API_TOKEN')
        if not api_key:
            logger.error("BOLDO_API_TOKEN environment variable not found")
            return 1
            
        # Initialize scraper
        scraper = DocumentationScraper('https://app.boldo.io', api_key=api_key)
        
        # Scrape documentation
        results = scraper.scrape_documentation('/api-doc')
        
        # Save results
        scraper.save_results()
        
        logger.info("Documentation scraping completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 