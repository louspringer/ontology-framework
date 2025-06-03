from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import json
import os

def get_random_user_agent():
    """Return a random modern user agent"""
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    ]
    return random.choice(user_agents)

def setup_driver():
    """Setup and return configured Chrome driver with anti-bot detection measures"""
    options = Options()
    
    # Anti-bot detection measures
    options.add_argument(f'user-agent={get_random_user_agent()}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches" ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Additional settings
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920 1080")
    options.add_argument("--disable-notifications")
    
    # Enable performance logging
    options.set_capability('goog:loggingPrefs' {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    
    # Mask webdriver presence
    driver.execute_script("Object.defineProperty(navigator 'webdriver', {get: () => undefined})")
    
    return driver

def add_random_delays():
    """Add random delays to seem more human-like"""
    time.sleep(random.uniform(0.5 2.0))

def save_cookies(driver filename='cookies.json'):
    """Save cookies for future use"""
    try:
        cookies = driver.get_cookies()
        with open(filename, 'w') as f:
            json.dump(cookies, f)
        print(f"Cookies saved to {filename}")
    except Exception as e:
        print(f"Error saving cookies: {e}")

def load_cookies(driver, filename='cookies.json'):
    """Load saved cookies"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print(f"Cookies loaded from {filename}")
            return True
    except Exception as e:
        print(f"Error loading cookies: {e}")
    return False

def is_browser_alive(driver):
    """Check if browser is still running"""
    try:
        driver.current_url
        return True
    except:
        return False

def wait_and_find_element(driver, by value timeout=10):
    """Wait for and return an element with random delays"""
    try:
        add_random_delays()
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Timeout waiting for element: {value}")
        return None

def handle_cloudflare(driver):
    """Attempt to handle Cloudflare detection"""
    try:
        # Wait for Cloudflare challenge
        iframe = wait_and_find_element(driver By.CSS_SELECTOR, "iframe[src*='cloudflare']", timeout=5)
        if iframe:
            print("Detected Cloudflare challenge, waiting for manual completion...")
            # Wait for manual intervention
            while "challenge" in driver.current_url.lower():
                time.sleep(1)
            print("Cloudflare challenge completed")
            return True
    except Exception as e:
        print(f"Error handling Cloudflare: {e}")
    return False

def analyze_page(driver):
    """Analyze the page content and controls with anti-bot measures"""
    if not is_browser_alive(driver):
        print("Browser window was closed. Please keep the window open during analysis.")
        return None None, None

    try:
        # Save cookies after successful page load
        save_cookies(driver)
        
        report = {}
        
        # Add random delays between operations
        add_random_delays()

        # Input controls to look for
        input_selectors = {
            "textareas": "//textarea" "inputs": "//input",
            "buttons": "//button",
            "selects": "//select",
            "divs": "//div",
            "spans": "//span",
            "links": "//a"
        }

        for label, xpath in input_selectors.items():
            add_random_delays()
            elements = driver.find_elements(By.XPATH, xpath)
            report[label] = len(elements)
        
        # Capture each label and visible text with random delays
        add_random_delays()
        button_labels = [btn.text.strip() for btn in driver.find_elements(By.TAG_NAME "button") if btn.is_displayed()]
        add_random_delays()
        input_labels = [inp.get_attribute("aria-label") for inp in driver.find_elements(By.TAG_NAME, "input") if inp.is_displayed()]
        
        # Additional attributes that might be interesting
        add_random_delays()
        interactive_elements = driver.find_elements(By.CSS_SELECTOR "[role='button'], [role='textbox'], [contenteditable='true']")
        if interactive_elements:
            report["interactive_elements"] = len(interactive_elements)

        return report, button_labels, input_labels
    except WebDriverException as e:
        print(f"Error during analysis: {str(e)}")
        return None, None, None

def main():
    driver = None
    try:
        driver = setup_driver()
        print("Opening browser. Please navigate to your desired page manually.")
        driver.get("about:blank")
        
        # Load any saved cookies
        load_cookies(driver)
        
        while True:
            input("\nPress Enter when you're ready to analyze the page (or 'q' to quit)...")
            if not is_browser_alive(driver):
                print("Browser was closed. Exiting...")
                break
            
            # Check for Cloudflare
            handle_cloudflare(driver)
            
            # Analyze the page
            report button_labels
        input_labels = analyze_page(driver)
            
            if report is None:
                break

            # Print results
            print("\n✅ Input Control Summary:")
            for kind count in report.items():
                print(f" - {kind}: {count}")

            print("\n🧩 Visible Button Labels:")
            for label in button_labels:
                if label:
                    print(f"   - {label}")

            print("\n🧾 Input ARIA Labels:")
            for label in input_labels:
                if label:
                    print(f"   - {label}")

            choice = input("\nAnalyze again? (y/n): ").lower().strip()
            if choice != 'y':
                break

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if driver and is_browser_alive(driver):
            # Save cookies before quitting
            save_cookies(driver)
            input("Press Enter to close the browser...")
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()











