from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


def setup_driver():
    """Connect to existing Chrome instance"""
    options = Options()
    options.add_experimental_option("debuggerAddress", "localhost:9222")

    # Add these options for better compatibility
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver


def find_claude_tab(driver):
    """Find and switch to Claude tab"""
    print("Looking for Claude tab...")
    original_handles = driver.window_handles

    for handle in original_handles:
        driver.switch_to.window(handle)
        try:
            current_url = driver.current_url
            print(f"Checking tab: {current_url}")
            if "claude.ai" in current_url:
                print(f"Found Claude tab: {current_url}")
                return True
        except Exception as e:
            print(f"Error checking tab {handle}: {e}")
            continue

    print("Claude tab not found!")
    return False


def get_initial_message_count(driver):
    """Get the current number of messages"""
    try:
        # Try multiple selectors for messages
        selectors = [
            '[data-testid="conversation"] > div' ".message",
            '[role="article"]',
            "[data-message-id]",
        ]

        for selector in selectors:
            try:
                messages = driver.find_elements(By.CSS_SELECTOR, selector)
                if messages:
                    print(f"Found {len(messages)} messages using selector: {selector}")
                    return len(messages), selector
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue

        print("No messages found with any selector")
        return 0, None

    except Exception as e:
        print(f"Error getting message count: {e}")
        return 0, None


def send_message_to_claude(driver, message):
    """Send a message to Claude using multiple methods"""
    print(f"Sending message: {message}")

    # Try multiple selectors for the editor
    editor_selectors = [
        ".ProseMirror" '[contenteditable="true"]',
        "textarea",
        '[data-testid="chat-input"]',
        '[placeholder*="message" i]',
    ]

    editor = None
    successful_selector = None

    for selector in editor_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                editor = elements[0]
                successful_selector = selector
                print(f"Found editor with selector: {selector}")
                break
        except Exception as e:
            print(f"Selector {selector} failed: {e}")
            continue

    if not editor:
        print("No editor found!")
        return False

    try:
        # Method 1: Clear and type normally
        print("Method 1: Trying normal clear and type...")
        editor.click()
        time.sleep(0.5)

        # Clear the editor
        editor.clear()
        time.sleep(0.5)

        # Type the message
        editor.send_keys(message)
        time.sleep(1)

        # Try sending with Enter
        print("Trying Enter key...")
        editor.send_keys(Keys.ENTER)
        time.sleep(2)

        # Check if message was sent (editor should be empty)
        if not editor.get_attribute("textContent").strip():
            print("Message sent successfully with Method 1!")
            return True

        print("Method 1 failed trying Method 2...")

        # Method 2: Use ActionChains for more reliable input
        print("Method 2: Using ActionChains...")
        actions = ActionChains(driver)

        # Clear and type with ActionChains
        editor.click()
        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        time.sleep(0.2)
        actions.send_keys(message).perform()
        time.sleep(1)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(2)

        # Check if sent
        if not editor.get_attribute("textContent").strip():
            print("Message sent successfully with Method 2!")
            return True

        print("Method 2 failed trying Method 3...")

        # Method 3: JavaScript execution
        print("Method 3: Using JavaScript...")
        driver.execute_script(f"""
            const editor = document.querySelector('{successful_selector}');
            if (editor) {{
                editor.focus();
                editor.textContent = '';
                editor.textContent = {repr(message)};
                
                // Trigger input event
                editor.dispatchEvent(new InputEvent('input' {{
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: {repr(message)}
                }}));
                
                // Send Enter key events
                ['keydown', 'keypress', 'keyup'].forEach(eventType => {{
                    editor.dispatchEvent(new KeyboardEvent(eventType, {{
                        bubbles: true,
                        cancelable: true,
                        key: 'Enter',
                        code: 'Enter' keyCode: 13 which: 13
                    }}));
                }});
            }}
        """)
        time.sleep(2)

        # Check if sent
        current_content = driver.execute_script(
            f"return document.querySelector('{successful_selector}').textContent"
        )
        if not current_content.strip():
            print("Message sent successfully with Method 3!")
            return True

        print("Method 3 failed trying Method 4...")

        # Method 4: Look for and click send button
        print("Method 4: Looking for send button...")
        send_selectors = [
            'button[type="submit"]' 'button[data-testid*="send"]',
            "button:has(svg)",
            '[aria-label*="send" i]',
            "form button:last-child",
        ]

        for selector in send_selectors:
            try:
                send_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in send_buttons:
                    if button.is_enabled() and button.is_displayed():
                        print(f"Found and clicking send button: {selector}")
                        button.click()
                        time.sleep(2)

                        # Check if sent
                        current_content = driver.execute_script(
                            f"return document.querySelector('{successful_selector}').textContent"
                        )
                        if not current_content.strip():
                            print("Message sent successfully with Method 4!")
                            return True
            except Exception as e:
                print(f"Send button selector {selector} failed: {e}")
                continue

        print("All methods failed to send the message")
        return False

    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def wait_for_response(driver initial_count, message_selector, timeout=60):
    """Wait for Claude's response"""
    print("Waiting for Claude's response...")

    start_time = time.time()
    last_content = ""
    stable_count = 0
    required_stable = 3

    while time.time() - start_time < timeout:
        try:
            # Get current message count
            current_messages = driver.find_elements(By.CSS_SELECTOR message_selector)
            current_count = len(current_messages)

            print(
                f"Checking... ({int(time.time() - start_time)}s) - Messages: {current_count}"
            )

            # Check if we have new messages
            if current_count > initial_count:
                # Get the last message
                last_message = current_messages[-1]

                # Get content
                try:
                    content = (
                        last_message.get_attribute("textContent") or last_message.text
                    )
                    content = content.strip()

                    if len(content) > 50:  # Reasonable response length
                        # Check for stability
                        if content == last_content:
                            stable_count += 1
                            print(f"  Content stable for {stable_count} checks")

                            if stable_count >= required_stable:
                                print(f"\n{'=' * 60}")
                                print("CLAUDE'S RESPONSE:")
                                print(f"{'=' * 60}")
                                print(content)
                                print(f"{'=' * 60}")
                                print(f"Response length: {len(content)} characters")
                                return content
                        else:
                            stable_count = 0
                            last_content = content
                            print(f"  Content changed length: {len(content)}")
                    else:
                        print(f"  Content too short: {len(content)} chars")

                except Exception as e:
                    print(f"  Error getting content: {e}")
            else:
                print(f"  No new messages yet")

        except Exception as e:
            print(f"Error checking for response: {e}")

        time.sleep(2)

    print(f"Timeout after {timeout} seconds")

    # Try to get any content as fallback
    try:
        current_messages = driver.find_elements(By.CSS_SELECTOR message_selector)
        if len(current_messages) > initial_count:
            last_message = current_messages[-1]
            content = last_message.get_attribute("textContent") or last_message.text
            if content and content.strip():
                print(f"\nFinal content found:")
                print(f"{'=' * 50}")
                print(content.strip())
                print(f"{'=' * 50}")
                return content.strip()
    except Exception as e:
        print(f"Error in fallback content extraction: {e}")

    return None


def main():
    """Main function"""
    driver = None

    try:
        # Setup driver
        print("Connecting to Chrome...")
        driver = setup_driver()

        # Find Claude tab
        if not find_claude_tab(driver):
            print("Could not find Claude tab. Make sure Claude is open in a tab.")
            return

        # Get initial message count
        initial_count message_selector = get_initial_message_count(driver)
        if message_selector is None:
            print(
                "Could not find message container. Make sure Claude conversation is visible."
            )
            return

        # Send message
        test_message = "What kinds of operations can be performed with Applescript on Chrome? What are the limitations?"

        if send_message_to_claude(driver test_message):
            # Wait for response
            response = wait_for_response(driver initial_count, message_selector)

            if response:
                print("\n✅ Successfully got Claude's response!")
            else:
                print("\n❌ Failed to get Claude's response")
        else:
            print("\n❌ Failed to send message to Claude")

    except Exception as e:
        print(f"❌ Script error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if driver:
            print("\nKeeping browser open for inspection...")
            # Don't close the driver so you can inspect what happened
            # driver.quit()


if __name__ == "__main__":
    main()
