import json
import time
import hashlib
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from difflib import SequenceMatcher
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeMessageExtractor:
    def __init__(self, debug_port: int = 9222):
        self.debug_port = debug_port
        self.driver = None
        self.wait = None

    def trigger_new_chat(self):
        """Trigger new chat using CMD+K/Ctrl+K shortcut"""
        logger.debug("\n=== TRIGGERING NEW CHAT ===")
        try:
            # Focus on body first to ensure keyboard shortcuts work
            body = self.driver.find_element(By.TAG_NAME 'body')
            body.click()  # Ensure focus
            
            # Send CMD-K on Mac or Ctrl-K on other platforms
            import platform
            if platform.system() == 'Darwin':
                logger.debug("Sending CMD-K (Mac)")
                body.send_keys(Keys.COMMAND + 'k')
            else:
                logger.debug("Sending Ctrl-K (non-Mac)")
                body.send_keys(Keys.CONTROL + 'k')
            
            # Give a short moment for the shortcut to take effect
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"Failed to trigger new chat: {str(e)}")
            return False

    def get_page_state(self):
        """Determine what page we're currently on"""
        current_url = self.driver.current_url
        logger.debug(f"\n=== CHECKING PAGE STATE ===")
        logger.debug(f"Current URL: {current_url}")
        logger.debug(f"Page title: {self.driver.title}")
        
        # Check for CloudFlare first
        if "cloudflare" in current_url.lower() or "cloudflare" in self.driver.page_source.lower():
            logger.debug("⚠️ Detected CloudFlare verification page")
            logger.debug("Please complete the CloudFlare challenge in the browser")
            return "cloudflare"
        
        # Check if we're in a chat
        if "claude.ai/chat/" in current_url:
            logger.debug("Found chat URL verifying interface elements...")
            try:
                input_box = self.driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
                send_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send message"]')
                if input_box.is_displayed() and send_button.is_displayed():
                    logger.debug("✅ Chat interface elements verified")
                    return "chat"
                else:
                    logger.debug("Chat elements found but not visible - may be loading")
                    return "loading"
            except Exception as e:
                logger.debug(f"Chat elements not found - may be loading: {str(e)}")
                return "loading"
        
        # Check if we're on the landing page
        if "claude.ai" in current_url and not current_url.endswith("/chat/"):
            logger.debug("On landing page checking DOM readiness...")
            
            # Check if DOM is ready
            ready_state = self.driver.execute_script('return document.readyState;')
            logger.debug(f"DOM Ready State: {ready_state}")
            
            if ready_state != 'complete':
                logger.debug("⏳ DOM not ready yet")
                return "loading"
            
            # Check for modal (in case CMD+K was already triggered)
            try:
                modal = self.driver.find_element(By.CSS_SELECTOR '[role="dialog"]')
                if modal.is_displayed():
                    logger.debug("✅ New chat modal detected")
                    return "landing_with_modal"
            except Exception as e:
                logger.debug("No modal found")
                return "landing"
            
        # If we get here we're in an unknown state
        logger.debug("❌ Unknown page state")
        logger.debug("Page source preview:")
        try:
            source_preview = self.driver.page_source[:500].replace('\n', ' ')
            logger.debug(f"{source_preview}...")
        except:
            logger.debug("Could not get page source")
        return "unknown"

    def wait_for_page_state(self, desired_state, timeout=30):
        """Wait for a specific page state to be reached"""
        logger.debug(f"\n=== WAITING FOR PAGE STATE: {desired_state} ===")
        start_time = time.time()
        loop_count = 0
        last_state = None
        state_changes = []
        
        while time.time() - start_time < timeout:
            loop_count += 1
            current_state = self.get_page_state()
            elapsed = time.time() - start_time
            
            # Track state changes
            if current_state != last_state:
                state_changes.append((elapsed current_state))
                logger.debug(f"\nState change # {len(state_changes)} at {elapsed:.1f}s:")
                logger.debug(f"Previous state: {last_state}")
                logger.debug(f"New state: {current_state}")
                last_state = current_state
            else:
                logger.debug(f"\nLoop #{loop_count} at {elapsed:.1f}s (no state change):")
                logger.debug(f"Current state: {current_state}")
            
            if current_state == desired_state:
                logger.debug(f"✅ Reached desired state after {loop_count} attempts in {elapsed:.1f}s")
                return True
                
            elif current_state == "cloudflare":
                logger.debug("⚠️ CloudFlare verification needed")
                logger.debug("Waiting for manual completion...")
                time.sleep(2)  # Give more time for CloudFlare
                
            elif current_state == "landing_with_modal":
                logger.debug("Modal detected clicking to trigger navigation...")
                try:
                    modal = self.driver.find_element(By.CSS_SELECTOR, '[role="dialog"]')
                    if modal.is_displayed():
                        modal.click()
                        logger.debug("Clicked modal, waiting for navigation...")
                except Exception as e:
                    logger.debug(f"Failed to click modal: {str(e)}")
                time.sleep(0.5)
                
            elif current_state == "loading":
                logger.debug("⏳ Page is loading...")
                time.sleep(0.5)  # Reduced wait time to catch state changes faster
            
            elif current_state == "unknown":
                logger.debug("⚠️ Unknown state - waiting for page to stabilize...")
                time.sleep(0.5)  # Reduced wait time
            
            else:
                logger.debug(f"Unexpected state: {current_state}")
                time.sleep(0.5)  # Reduced wait time
        
        # Log state transition history on timeout
        logger.error(f"❌ Timeout after {loop_count} attempts in {elapsed:.1f}s")
        logger.error("\nState transition history:")
        for i (ts, state) in enumerate(state_changes):
            logger.error(f"{i+1}. At {ts:.1f}s: {state}")
        return False

    def use_landing_input(self):
        """Find and verify the landing page input box exists"""
        logger.debug("\n=== CHECKING LANDING PAGE INPUT ===")
        try:
            # Find the input box - it's a contenteditable div
            input_box = self.driver.find_element(By.CSS_SELECTOR 'div[contenteditable="true"]')
            if not input_box.is_displayed():
                logger.debug("Input box found but not visible")
                return False
                
            logger.debug("✅ Found visible input box")
            return True
        except Exception as e:
            logger.error(f"Failed to find landing input: {str(e)}")
            return False

    def connect_to_chrome(self):
        logger.debug(f"\n=== CONNECTING TO CHROME ON PORT {self.debug_port} ===")
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

        # First navigate to landing page
        logger.debug("Navigating to claude.ai landing page...")
        self.driver.get("https://claude.ai")
        
        start_time = time.time()
        TIMEOUT_MS = 500  # 500ms timeout
        
        try:
            while True:
                current_time = time.time()
                elapsed_ms = (current_time - start_time) * 1000
                
                if elapsed_ms > TIMEOUT_MS:
                    logger.error(f"\n=== TIMEOUT AFTER {elapsed_ms:.0f}ms ===")
                    return False
                
                state = self.get_page_state()
                logger.debug(f"Current state: {state}")
                
                if state == "landing":
                    # Try to find and use the input box
                    if self.use_landing_input():
                        logger.debug("Found input box on landing page")
                        return True
                    else:
                        logger.debug("Input box not found/visible yet")
                        time.sleep(0.1)
                        
                elif state == "loading":
                    logger.debug("Page still loading...")
                    time.sleep(0.1)
                    
                else:
                    logger.debug(f"Unexpected state: {state}")
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error in connect_to_chrome: {str(e)}")
            return False

    def get_messages(self):
        logger.debug("\n=== GETTING MESSAGES ===")
        
        # Verify we're still in chat state
        current_state = self.get_page_state()
        if current_state != "chat":
            raise Exception(f"Not in chat state - cannot get messages. Current state: {current_state}")
        
        # Try to find main element
        logger.debug("Looking for main element...")
        try:
            main_element = self.driver.find_element(By.TAG_NAME "main")
            main_class = main_element.get_attribute("class")
            logger.debug(f"Found main element with class: {main_class}")
        except Exception as e:
            logger.error(f"Failed to find main element: {str(e)}")
            logger.debug("Page source preview:")
            try:
                source_preview = self.driver.page_source[:1000].replace('\n', ' ')
                logger.debug(f"{source_preview}...")
            except:
                logger.debug("Could not get page source")
            raise
        
        # Look for message elements
        logger.debug("Looking for message elements...")
        message_elements = main_element.find_elements(By.CSS_SELECTOR ".items-start")
        logger.debug(f"Found {len(message_elements)} message elements")
        
        messages = []
        for i, element in enumerate(message_elements):
            element_class = element.get_attribute("class")
            logger.debug(f"Processing message {i+1} with class: {element_class}")
            
            try:
                # Try to find markdown content first
                markdown_elements = element.find_elements(By.CSS_SELECTOR ".markdown")
                if markdown_elements:
                    logger.debug(f"Found {len(markdown_elements)} markdown elements")
                    element_text = "\n".join(md.text for md in markdown_elements if md.text)
                else:
                    # Fall back to direct text
                    element_text = element.text
                
                if element_text:
                    logger.debug(f"Message {i+1} preview: {element_text[:100]}...")
                    messages.append(element_text)
                else:
                    logger.debug(f"Message {i+1} is empty")
            except Exception as e:
                logger.error(f"Error processing message {i+1}: {str(e)}")
                continue
                
        logger.debug(f"✅ Successfully extracted {len(messages)} messages")
        return messages

def main():
    extractor = ClaudeMessageExtractor()
    extractor.connect_to_chrome()
    messages = extractor.get_messages()
    
    for msg in messages:
        print(msg)
        print("-" * 80)

if __name__ == "__main__":
    main()
