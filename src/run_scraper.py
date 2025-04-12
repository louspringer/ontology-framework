import logging
import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scraper')

def main():
    load_dotenv()
    api_key = os.getenv('BOLDO_API_TOKEN')
    if not api_key:
        logger.error("BOLDO_API_TOKEN environment variable not found in .env file")
        logger.debug("Available environment variables: %s", list(os.environ.keys()))
        return
    
    logger.info(f"API key loaded successfully: {api_key[:8]}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the documentation page
            logger.info("Navigating to documentation page")
            page.goto('https://app.boldo.io/en/api-doc')
            
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
                auth_button = page.get_by_role("button", name="Authenticate")
                logger.info("Found Authenticate button, clicking it")
                auth_button.click()
                
                # Wait for and fill the API key input
                logger.info("Waiting for API key input field")
                api_key_input = page.get_by_label("API key")
                logger.info("Found API key input field")
                api_key_input.fill(api_key)
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
            
            # Extract endpoints
            endpoints = []
            for endpoint in page.query_selector_all('[data-sentry-component$="Query"]'):
                # Log the HTML structure for debugging
                logger.debug("Endpoint HTML structure:")
                logger.debug(endpoint.inner_html())
                
                # Click the expander to show full details
                expander = endpoint.query_selector('button[aria-expanded="false"]')
                if expander:
                    logger.info("Expanding endpoint details")
                    expander.click()
                    # Wait a short time for the animation
                    time.sleep(1)
                    
                    # Log the expanded HTML structure
                    logger.debug("Expanded endpoint HTML structure:")
                    logger.debug(endpoint.inner_html())
                
                header = endpoint.query_selector('[data-sentry-component="ApiQueryHeader"]')
                if header:
                    method = header.query_selector('.text-md.rounded-md').inner_text()
                    path = header.query_selector('.text-md.select-text').inner_text()
                    description = header.query_selector('.text-sm.font-normal').inner_text()
                    
                    # Get the execute button if present
                    execute_button = endpoint.query_selector('button:has-text("Execute")')
                    execute_available = execute_button is not None
                    
                    # Get the full endpoint details
                    details = {
                        'method': method,
                        'path': path,
                        'description': description,
                        'execute_available': execute_available
                    }
                    
                    # If there's an execute button, get the request/response details
                    if execute_available:
                        # Get request parameters
                        params_section = endpoint.query_selector('div[class*="parameters"]')
                        if params_section:
                            params = []
                            for param in params_section.query_selector_all('div[class*="parameter"]'):
                                try:
                                    param_name = param.query_selector('span[class*="name"]').inner_text()
                                    param_type = param.query_selector('span[class*="type"]').inner_text()
                                    param_required = param.query_selector('span[class*="required"]') is not None
                                    params.append({
                                        'name': param_name,
                                        'type': param_type,
                                        'required': param_required
                                    })
                                except Exception as e:
                                    logger.warning(f"Error extracting parameter: {e}")
                                    continue
                            details['parameters'] = params
                        
                        # Get response details
                        response_section = endpoint.query_selector('div[class*="response"]')
                        if response_section:
                            try:
                                response_type = response_section.query_selector('span[class*="type"]').inner_text()
                                response_example = response_section.query_selector('pre').inner_text()
                                details['response'] = {
                                    'type': response_type,
                                    'example': response_example
                                }
                            except Exception as e:
                                logger.warning(f"Error extracting response: {e}")
                    
                    endpoints.append(details)
            
            if endpoints:
                logger.info("Found API endpoints:")
                for endpoint in endpoints:
                    logger.info(f"\n{endpoint['method']} {endpoint['path']}")
                    logger.info(f"Description: {endpoint['description']}")
                    logger.info(f"Execute available: {endpoint['execute_available']}")
                    if 'parameters' in endpoint:
                        logger.info("Parameters:")
                        for param in endpoint['parameters']:
                            logger.info(f"  - {param['name']} ({param['type']}) {'[Required]' if param['required'] else ''}")
                    if 'response' in endpoint:
                        logger.info(f"Response type: {endpoint['response']['type']}")
                        logger.info(f"Response example: {endpoint['response']['example']}")
                    logger.info("---")
            else:
                logger.error("No API endpoints found")
                page_content = page.content()
                logger.error("Page content:")
                logger.error(page_content[:2000])  # Log first 2000 chars to avoid overwhelming logs
                
        except Exception as e:
            logger.error(f"Failed to scrape documentation: {str(e)}")
            raise
        finally:
            browser.close()

if __name__ == "__main__":
    main() 