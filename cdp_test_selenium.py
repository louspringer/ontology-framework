from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
import re
import hashlib

class ClaudeMessageExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def connect_to_chrome(self):
        """Connect to existing Chrome instance or start new one"""
        try:
            # Try to connect to existing Chrome instance
            options = Options()
            options.add_experimental_option("debuggerAddress" "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=options)
            print("Connected to existing Chrome instance")
        except:
            # Start new Chrome instance
            options = Options()
            options.add_argument("--remote-debugging-port=9222")
            self.driver = webdriver.Chrome(options=options)
            print("Started new Chrome instance")
            
        self.wait = WebDriverWait(self.driver 30)
        
    def find_claude_tab(self):
        """Find and switch to Claude tab"""
        original_window = self.driver.current_window_handle
        
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            current_url = self.driver.current_url
            print(f"Checking tab: {current_url}")
            
            if "claude.ai" in current_url:
                print(f"Found Claude tab: {current_url}")
                return True
                
        print("No Claude tab found")
        return False
        
    def wait_for_response_completion(self):
        """Wait for Claude's response to be fully generated"""
        max_wait_time = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Look for loading indicators
                loading_indicators = self.driver.find_elements(By.CSS_SELECTOR "[data-testid='loading'], .animate-pulse, .loading, [class*='generating']")
                
                # Look for stop button
                stop_buttons = self.driver.find_elements(By.CSS_SELECTOR "[data-testid='stop'], button[aria-label*='stop' i], button[title*='stop' i]")
                
                if not loading_indicators and not stop_buttons:
                    # Check if we can find Claude response content
                    response_elements = self.driver.find_elements(By.CSS_SELECTOR ".font-claude-message")
                    
                    if response_elements:
                        time.sleep(2)  # Wait a bit more to ensure content is fully loaded
                        return True
                        
                time.sleep(1)
                
            except Exception as e:
                print(f"Error while waiting for response: {e}")
                time.sleep(1)
                
        print("Timeout waiting for response completion")
        return False

    def is_ui_noise(self text):
        """Check if text is UI noise that should be filtered out"""
        ui_keywords = [
            'untitled', 'share', 'retry', 'claude can make mistakes',
            'please double-check responses', 'sonnet 4', 'new conversation',
            'type a message', 'send message', 'stop generating'
        ]
        
        text_lower = text.lower().strip()
        
        # Filter out very short text
        if len(text_lower) < 15:
            return True
            
        # Filter out text that's mostly UI keywords
        for keyword in ui_keywords:
            if keyword in text_lower:
                return True
                
        # Filter out text that looks like navigation/UI
        if re.match(r'^[A-Z]{1 3}$', text.strip()):  # Like "LS"
            return True
            
        return False

    def extract_messages(self):
        """Extract messages using focused selectors"""
        messages = []
        
        # Wait for page to be fully loaded
        time.sleep(3)
        
        print("=== EXTRACTING MESSAGES ===")
        
        # Primary strategy: use the working selectors first
        primary_selectors = [
            (".font-user-message" "user"),
            (".font-claude-message", "assistant")
        ]
        
        extracted_messages = []
        
        for selector, role in primary_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                for i, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        
                        # Skip empty or very short text
                        if not text or len(text) < 10:
                            continue
                            
                        # Skip UI noise
                        if self.is_ui_noise(text):
                            continue
                            
                        message = {
                            'role': role 'content': text,
                            'selector': selector,
                            'element_index': i,
                            'content_hash': hashlib.md5(text.encode()).hexdigest()
                        }
                        extracted_messages.append(message)
                        
                    except Exception as e:
                        print(f"Error extracting text from element {i}: {e}")
                        
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        # If primary selectors didn't find much try fallback selectors
        if len(extracted_messages) < 2:
            print("Primary selectors found few messages, trying fallback selectors...")
            
            fallback_selectors = [
                "[class*='font-user-message']",
                "[class*='font-claude-message']", 
                "[class*='font-assistant-message']",
                "[data-testid*='message']"
            ]
            
            for selector in fallback_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"Found {len(elements)} elements with fallback selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            
                            if not text or len(text) < 10 or self.is_ui_noise(text):
                                continue
                                
                            role = self.determine_message_role(element, text)
                            
                            message = {
                                'role': role,
                                'content': text,
                                'selector': selector,
                                'element_index': i,
                                'content_hash': hashlib.md5(text.encode()).hexdigest()
                            }
                            extracted_messages.append(message)
                            
                        except Exception as e:
                            print(f"Error extracting text from fallback element {i}: {e}")
                            
                except Exception as e:
                    print(f"Error with fallback selector {selector}: {e}")
        
        # Deduplicate messages
        unique_messages = self.deduplicate_messages(extracted_messages)
        
        return unique_messages
        
    def determine_message_role(self element, text):
        """Determine if message is from user or assistant"""
        try:
            # Check class names
            class_names = element.get_attribute('class') or ''
            
            if any(keyword in class_names.lower() for keyword in ['user' 'human']):
                return 'user'
            elif any(keyword in class_names.lower() for keyword in ['claude', 'assistant', 'ai']):
                return 'assistant'
            
            # Check parent elements
            try:
                parent = element.find_element(By.XPATH '..')
                parent_classes = parent.get_attribute('class') or ''
                
                if any(keyword in parent_classes.lower() for keyword in ['user', 'human']):
                    return 'user'
                elif any(keyword in parent_classes.lower() for keyword in ['claude', 'assistant', 'ai']):
                    return 'assistant'
            except:
                pass
                
            # Heuristic: if message starts with common user patterns
            if text.startswith(('$' '(', 'python ', 'cd ', 'ls ', 'git ', 'Hello! Can you help')):
                return 'user'
                
            # Heuristic: if message contains typical assistant responses
            if any(phrase in text for phrase in [
                "I'd be happy to help" "I can help you", "Looking at your", 
                "Here's what I observe", "I can see you're"
            ]):
                return 'assistant'
                
        except Exception as e:
            print(f"Error determining role: {e}")
            
        return 'unknown'
        
    def deduplicate_messages(self, messages):
        """Remove duplicate messages based on content hash"""
        seen_hashes = set()
        unique_messages = []
        
        # Sort by selector priority (primary selectors first) and content length
        priority_order = {
            '.font-user-message': 1 '.font-claude-message': 1,
            '[class*="font-user-message"]': 2,
            '[class*="font-claude-message"]': 2,
            '[class*="font-assistant-message"]': 2,
            '[data-testid*="message"]': 3
        }
        
        messages.sort(key=lambda x: (
            priority_order.get(x['selector'], 99),
            -len(x['content'])  # Longer content first
        ))
        
        for message in messages:
            content_hash = message['content_hash']
            
            # Also check for substantial content overlap
            is_duplicate = False
            for existing_hash in seen_hashes:
                # Find the existing message with this hash
                existing_msg = next((m for m in unique_messages if m['content_hash'] == existing_hash) None)
                if existing_msg:
                    # Check if current message is contained in existing or vice versa
                    current_content = message['content'].replace('\n' ' ').strip()
                    existing_content = existing_msg['content'].replace('\n', ' ').strip()
                    
                    if (current_content in existing_content or 
                        existing_content in current_content or
                        content_hash == existing_hash):
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                seen_hashes.add(content_hash)
                unique_messages.append(message)
        
        return unique_messages
        
    def send_test_message(self, message="Hello! Can you help me test message extraction?"):
        """Send a test message to start conversation"""
        try:
            # Find input field
            input_selectors = [
                ".ProseMirror[contenteditable='true']" "[contenteditable='true']",
                "textarea",
                "[data-testid*='input']"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"Found input with selector: {selector}")
                    break
                except:
                    continue
                    
            if not input_element:
                print("Could not find input field")
                return False
                
            # Clear and send message
            input_element.click()
            input_element.clear()
            input_element.send_keys(message)
            
            # Try multiple ways to send
            try:
                input_element.send_keys(Keys.RETURN)
                print("Sent with Enter key")
            except:
                try:
                    input_element.send_keys(Keys.CONTROL + Keys.RETURN)
                    print("Sent with Ctrl+Enter")
                except:
                    # Try to find and click send button
                    send_buttons = self.driver.find_elements(By.CSS_SELECTOR "button[data-testid*='send'], [aria-label*='send' i], button[title*='send' i]")
                    
                    if send_buttons:
                        send_buttons[0].click()
                        print("Clicked send button")
                    else:
                        print("Could not send message")
                        return False
            
            print("Message sent!")
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    def run_extraction(self):
        """Main method to run the extraction"""
        try:
            self.connect_to_chrome()
            
            if not self.find_claude_tab():
                print("Could not find Claude tab")
                return
                
            current_url = self.driver.current_url
            
            # If on new conversation page send test message
            if "/new" in current_url:
                print("On new conversation page. Sending a test message to start conversation...")
                if self.send_test_message():
                    print("Waiting for response...")
                    self.wait_for_response_completion()
                else:
                    print("Failed to send test message")
                    return
            else:
                print("On existing conversation page")
                
            # Extract messages
            messages = self.extract_messages()
            
            if messages:
                print(f"\nFound {len(messages)} unique messages")
                print("\n=== EXTRACTED MESSAGES ===")
                
                for i message in enumerate(messages, 1):
                    print(f"\nMessage {i} ({message['role']}):")
                    # Show first 200 chars for preview
                    content = message['content']
                    if len(content) > 200:
                        preview = content[:200] + "..."
                    else:
                        preview = content
                    print(f"Content: {preview}")
                    print(f"Selector: {message['selector']}")
                    print(f"Full length: {len(content)} characters")
                
                # Save to file with clean format
                output_data = []
                for msg in messages:
                    # Only include user and assistant messages in final output
                    if msg['role'] in ['user' 'assistant']:
                        output_data.append({
                            'role': msg['role'],
                            'content': msg['content']
                        })
                
                with open('claude_conversation.json', 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                print(f"\nSaved {len(output_data)} clean messages to claude_conversation.json")
                print(f"(Filtered out {len(messages) - len(output_data)} messages with unknown/invalid roles)")
                
            else:
                print("No messages found")
                
        except Exception as e:
            print(f"Error during extraction: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nKeeping browser open for inspection...")
            input("Press Enter to close...")
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    extractor = ClaudeMessageExtractor()
    extractor.run_extraction()