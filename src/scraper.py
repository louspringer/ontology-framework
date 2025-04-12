# This file is now deprecated as functionality has moved to run_scraper.py
import logging
import requests
from bs4 import BeautifulSoup
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scraper')

class Scraper:
    """Deprecated: Functionality has moved to run_scraper.py"""
    def __init__(self):
        logger.warning("This Scraper class is deprecated. Please use run_scraper.py directly.")
        load_dotenv()
        self.api_key = os.getenv('BOLDO_API_TOKEN')
        if not self.api_key:
            logger.error("BOLDO_API_TOKEN environment variable not found in .env file")
            logger.debug("Available environment variables: %s", list(os.environ.keys()))
            raise ValueError("BOLDO_API_TOKEN environment variable not found")
        logger.info("API key loaded successfully: %s...", self.api_key[:8])

    def scrape_documentation(self) -> Optional[Dict[str, Any]]:
        """
        Scrape API documentation using browser automation.
        This implementation:
        1. Checks session storage for existing auth
        2. Handles the modal popup correctly
        3. Uses proper selectors for the API key input
        4. Has better error handling and logging
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the documentation page
                logger.info("Navigating to documentation page")
                page.goto('https://app.boldo.ai/en/api-doc')
                
                # Wait for initial page load
                logger.info("Waiting for page to load")
                page.wait_for_selector('h1:has-text("Alpha API")')
                
                # Check if already authenticated
                logger.info("Checking session storage for auth")
                auth_state = page.evaluate('() => window.sessionStorage.getItem("auth")')
                
                if not auth_state:
                    logger.info("No auth found, attempting to authenticate")
                    
                    # Look for and click the Authenticate button
                    logger.info("Looking for Authenticate button")
                    auth_button = page.get_by_text("Authenticate")
                    logger.info("Found Authenticate button, clicking it")
                    auth_button.click()
                    
                    # Wait for and fill the API key input
                    logger.info("Waiting for API key input field")
                    api_key_input = page.get_by_label("API key")
                    logger.info("Found API key input field")
                    api_key_input.fill(self.api_key)
                    api_key_input.press('Enter')
                
                # Wait for content to load
                logger.info("Waiting for content to load")
                time.sleep(2)  # Give time for client-side rendering
                
                # Get the page title
                title = page.title()
                logger.info(f"Page title: {title}")
                
                # Look for API endpoints
                logger.info("Looking for API endpoints")
                
                # Wait for the accordion items to be present
                page.wait_for_selector('[data-sentry-component$="Query"]')
                
                # Extract API endpoints
                endpoints = []
                endpoint_elements = page.query_selector_all('div[class*="endpoint"]')
                for element in endpoint_elements:
                    try:
                        title = element.query_selector('h3')
                        description = element.query_selector('p')
                        method = element.query_selector('span[class*="method"]')
                        path = element.query_selector('span[class*="path"]')
                        
                        endpoint = {
                            'title': title.inner_text() if title else '',
                            'description': description.inner_text() if description else '',
                            'method': method.inner_text() if method else '',
                            'path': path.inner_text() if path else ''
                        }
                        endpoints.append(endpoint)
                    except Exception as e:
                        logger.error(f"Error extracting endpoint: {e}")
                        continue
                
                if endpoints:
                    logger.info("Found API endpoints:")
                    for endpoint in endpoints:
                        logger.info(f"{endpoint['method']} {endpoint['path']}")
                        logger.info(f"Description: {endpoint['description']}\n")
                    return {
                        'title': title,
                        'endpoints': endpoints
                    }
                else:
                    logger.error("No API endpoints found")
                    page_content = page.content()
                    logger.error("Page content:")
                    logger.error(page_content[:2000])  # Log first 2000 chars to avoid overwhelming logs
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to scrape documentation: {str(e)}")
                raise
            finally:
                browser.close()

    def _try_direct_auth(self, session: requests.Session) -> Optional[Dict[str, Any]]:
        """Try direct authentication using API key in header"""
        logger.info("Attempting direct authentication with API key in header...")
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            response = session.get('https://app.boldo.io/api-doc', headers=headers)
            logger.info(f"Direct auth response status: {response.status_code}")
            if response.status_code == 200:
                return self._parse_response(response)
            return None
        except Exception as e:
            logger.error(f"Direct auth failed: {str(e)}")
            return None

    def _try_form_auth(self, session: requests.Session) -> Optional[Dict[str, Any]]:
        """Try authentication by submitting API key via form"""
        logger.info("Attempting form authentication...")
        try:
            # Get initial page to obtain any CSRF tokens
            response = session.get('https://app.boldo.io/api-doc')
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Submit API key via form data
            form_data = {
                'apiKey': self.api_key,
                'submit': 'true'
            }
            
            response = session.post('https://app.boldo.io/api-doc', data=form_data)
            logger.info(f"Form auth response status: {response.status_code}")
            
            if response.status_code == 200:
                return self._parse_response(response)
            return None
        except Exception as e:
            logger.error(f"Form auth failed: {str(e)}")
            return None

    async def _try_browser_auth(self) -> Optional[Dict[str, Any]]:
        """Try authentication using browser automation with Playwright"""
        logger.info("Attempting browser authentication...")
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to the page
                await page.goto('https://app.boldo.io/api-doc')
                
                # Wait for and fill the API key input
                await page.wait_for_selector('input[type="text"]')
                await page.fill('input[type="text"]', self.api_key)
                
                # Submit the form
                await page.keyboard.press('Enter')
                
                # Wait for navigation
                await page.wait_for_load_state('networkidle')
                
                # Get the content
                content = await page.content()
                await browser.close()
                
                return self._parse_html_content(content)
        except Exception as e:
            logger.error(f"Browser auth failed: {str(e)}")
            return None

    def _parse_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """Parse the response and extract documentation content"""
        try:
            # Try parsing as JSON first
            try:
                return response.json()
            except:
                pass
                
            # If not JSON, parse HTML
            return self._parse_html_content(response.text)
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return None

    def _parse_html_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content and extract documentation"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Log the title for debugging
            title = soup.title.string if soup.title else "No title found"
            logger.info(f"Page title: {title}")
            
            # Try to find documentation content
            doc_container = soup.find('div', {'class': ['documentation', 'api-doc', 'swagger-ui']})
            if not doc_container:
                logger.error("Documentation container not found")
                return None
                
            return {
                'title': title,
                'content': doc_container.get_text(strip=True)
            }
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return None 