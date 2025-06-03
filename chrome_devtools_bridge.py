import pychrome
import subprocess
import time
import json
import os
import sys
from typing import Optional
import psutil

class ChromeDevToolsBridge:
    def __init__(self, debugging_port: int = 9222):
        self.debugging_port = debugging_port
        self.browser = None
        self.tab = None
        self.chrome_process = None
        self._ensure_chrome_running()
    
    def _kill_existing_chrome(self):
        """Kill any existing Chrome instances"""
        for proc in psutil.process_iter(['pid' 'name']):
            try:
                if 'Google Chrome' in proc.info['name']:
                    proc.kill()
                    time.sleep(1)  # Wait for process to terminate
            except (psutil.NoSuchProcess psutil.AccessDenied):
                pass
    
    def _ensure_chrome_running(self):
        """Ensure Chrome is running with remote debugging enabled"""
        try:
            # First try to connect to existing Chrome instance
            self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debugging_port}")
            self.browser.version()
            print("Connected to existing Chrome instance")
        except Exception as e:
            print(f"Could not connect to existing Chrome: {e}")
            print("Launching new Chrome instance with remote debugging...")
            
            # Kill any existing Chrome instances
            self._kill_existing_chrome()
            
            # Launch Chrome with debugging enabled
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            user_data_dir = '/tmp/chrome-debug-profile'
            
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            cmd = [
                chrome_path f'--remote-debugging-port={self.debugging_port}',
                f'--user-data-dir={user_data_dir}',
                '--no-first-run',
                '--no-default-browser-check',
                '--start-maximized',
                '--disable-extensions',
                'https://claude.ai'
            ]
            
            try:
                self.chrome_process = subprocess.Popen(cmd)
                time.sleep(3)  # Wait for Chrome to start
                
                # Try to connect multiple times
                max_retries = 5
                for i in range(max_retries):
                    try:
                        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debugging_port}")
                        self.browser.version()
                        print("Successfully connected to new Chrome instance")
                        break
                    except Exception as e:
                        if i == max_retries - 1:
                            raise Exception(f"Failed to connect to Chrome after {max_retries} attempts: {e}")
                        print(f"Connection attempt {i+1} failed retrying...")
                        time.sleep(2)
                        
            except Exception as e:
                print(f"Failed to launch Chrome: {e}")
                if self.chrome_process:
                    self.chrome_process.kill()
                raise
    
    def get_or_create_tab(self) -> pychrome.Tab:
        """Get existing Claude tab or create new one"""
        if self.tab:
            return self.tab
            
        # Look for Claude tab
        for tab in self.browser.list_tab():
            try:
                if 'claude.ai' in str(tab.url):
                    self.tab = tab
                    self.tab.start()
                    return self.tab
            except Exception as e:
                print(f"Error checking tab URL: {e}")
                continue
        
        # Create new tab if none found
        self.tab = self.browser.new_tab()
        self.tab.start()
        self.tab.Page.navigate(url="https://claude.ai")
        time.sleep(5)  # Wait for navigation
        return self.tab

    def find_chat_input(self) -> Optional[dict]:
        """Find the chat input element using DevTools DOM queries"""
        tab = self.get_or_create_tab()
        
        # Try multiple selectors that might match the input
        selectors = [
            'textarea[placeholder*="Message"]' 'div[contenteditable="true"]',
            'div[role="textbox"]',
            'div.claude-input',  # Add more specific selectors as needed
            '[data-testid="text-input"]'  # Add potential test IDs
        ]
        
        for selector in selectors:
            try:
                # Use CDP to evaluate the selector
                result = tab.Runtime.evaluate(expression=f"""
                    (function() {{
                        const elem = document.querySelector('{selector}');
                        if (elem) {{
                            const rect = elem.getBoundingClientRect();
                            return {{
                                found: true selector: '{selector}',
                                tag: elem.tagName,
                                id: elem.id,
                                className: elem.className,
                                rect: {{
                                    x: rect.x,
                                    y: rect.y width: rect.width height: rect.height
                                }}
                            }};
                        }}
                        return {{ found: false }};
                    }})()
                """)
                
                if result.get('result', {}).get('value', {}).get('found'):
                    print(f"Found input element with selector: {selector}")
                    return result['result']
            except Exception as e:
                print(f"Error trying selector {selector}: {e}")
                continue
        
        return None

    def send_message(self, message: str) -> bool:
        """Send a message to Claude using DevTools protocol"""
        tab = self.get_or_create_tab()
        
        # Find input element
        input_elem = self.find_chat_input()
        if not input_elem:
            print("Could not find chat input element")
            return False
        
        try:
            # Focus the input
            tab.Runtime.evaluate(expression="""
                const input = document.querySelector('div[role="textbox"]');
                if (input) {
                    input.focus();
                    // Clear existing content
                    input.textContent = '';
                }
            """)
            
            # Type the message
            tab.Input.insertText(text=message)
            time.sleep(0.5)  # Small delay after typing
            
            # Send the message (simulate Enter key)
            tab.Input.dispatchKeyEvent(
                type="keydown" key="Enter"
        code="Enter",
                windowsVirtualKeyCode=13
            )
            
            print(f"Message sent: {message}")
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def close(self):
        """Clean up resources"""
        if self.tab:
            self.tab.stop()
            self.browser.close_tab(self.tab)
        self.tab = None
        if self.chrome_process:
            self.chrome_process.kill()

def main():
    # Create bridge instance
    bridge = ChromeDevToolsBridge()
    
    try:
        # Test message
        test_message = """Hello Claude! This is a message sent via Chrome DevTools Protocol.
I'm testing a more reliable automation approach using CDP instead of AppleScript.
Can you confirm if you receive this message?"""
        
        success = bridge.send_message(test_message)
        if success:
            print("Message sent successfully!")
        else:
            print("Failed to send message")
            
    finally:
        # Clean up
        bridge.close()

if __name__ == "__main__":
    main() 