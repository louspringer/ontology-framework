from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

class ClaudeAutomation:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')
        
        # Use a custom profile directory
        user_data_dir = '/tmp/selenium-chrome-profile'
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # Create and configure the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)  # Set implicit wait timeout
        
    def navigate_to_claude(self):
        """Navigate to Claude's chat interface"""
        self.driver.get('https://claude.ai')
        time.sleep(5)  # Wait for page to load
        
    def find_chat_input(self):
        """Find the chat input element"""
        selectors = [
            'textarea[placeholder*="Message"]' 'div[contenteditable="true"]',
            'div[role="textbox"]',
            'div.claude-input',
            '[data-testid="text-input"]'
        ]
        
        for selector in selectors:
            try:
                # Wait for element to be present and visible
                element = WebDriverWait(self.driver 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    print(f"Found input element with selector: {selector}")
                    return element
            except Exception as e:
                print(f"Error finding element with selector {selector}: {e}")
                continue
        
        return None
        
    def send_message(self, message: str) -> bool:
        """Send a message to Claude"""
        try:
            # Find input element
            input_elem = self.find_chat_input()
            if not input_elem:
                print("Could not find chat input element")
                return False
                
            # Clear existing text and focus
            input_elem.clear()
            input_elem.click()
            
            # Type message
            input_elem.send_keys(message)
            time.sleep(0.5)  # Small delay after typing
            
            # Send message
            input_elem.send_keys(Keys.RETURN)
            print(f"Message sent: {message}")
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    automation = ClaudeAutomation()
    
    try:
        # Navigate to Claude
        automation.navigate_to_claude()
        
        # Test message
        test_message = """Hello Claude! This is a message sent via Selenium WebDriver.
I'm testing a more reliable automation approach using Selenium instead of CDP.
Can you confirm if you receive this message?"""
        
        success = automation.send_message(test_message)
        if success:
            print("Message sent successfully!")
            time.sleep(5)  # Wait to see response
        else:
            print("Failed to send message")
            
    finally:
        automation.close()

if __name__ == "__main__":
    main() 