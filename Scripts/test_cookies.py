import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_DIR = Path(__file__).parent.parent

def handle_cookie_banner(driver):
    """Handle cookie consent banner"""
    print("Checking for cookie banner...")
    
    # Common cookie accept button texts
    accept_texts = [
        "Accept", "Accept All", "Accept Cookies", "I Accept", "Agree", 
        "Got it", "Okay", "OK", "Allow", "Consent", "Continue"
    ]
    
    # Common cookie banner selectors
    banner_selectors = [
        "div.cookie-banner",
        "div.cookie-notice",
        "div[class*='cookie']",
        "div[class*='Cookie']",
        "div#cookie-banner",
        "div#cookie-notice",
        "div[data-testid='cookie-banner']",
        "div[role='alertdialog']",
        "div.consent-banner"
    ]
    
    try:
        # Wait for banner to appear
        wait = WebDriverWait(driver, 5)
        
        for selector in banner_selectors:
            try:
                banner = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"Found cookie banner with selector: {selector}")
                
                # Take screenshot of banner
                driver.save_screenshot(str(BASE_DIR / "data" / "cookie_banner.png"))
                print("Screenshot saved: data/cookie_banner.png")
                
                # Try different methods to find accept button
                accept_button = None
                
                # Method 1: Look for button with accept text
                for text in accept_texts:
                    try:
                        button = banner.find_element(
                            By.XPATH, f".//button[contains(text(), '{text}')]"
                        )
                        accept_button = button
                        print(f"Found accept button with text: '{text}'")
                        break
                    except:
                        continue
                
                # Method 2: Look for button with data attribute
                if not accept_button:
                    try:
                        accept_button = banner.find_element(
                            By.CSS_SELECTOR, "button[data-testid='accept-cookies'], button[data-cy='accept-cookies']"
                        )
                        print("Found accept button by data attribute")
                    except:
                        pass
                
                # Method 3: Look for any button in banner
                if not accept_button:
                    try:
                        buttons = banner.find_elements(By.TAG_NAME, "button")
                        if buttons:
                            accept_button = buttons[0]  # First button
                            print(f"Using first button in banner: '{accept_button.text}'")
                    except:
                        pass
                
                if accept_button:
                    accept_button.click()
                    print("Clicked accept button")
                    time.sleep(2)  # Wait for banner to disappear
                    return True
                else:
                    print("Could not find accept button in banner")
                    return False
                    
            except Exception as e:
                continue
        
        print("No cookie banner found or could not interact with it")
        return False
        
    except Exception as e:
        print(f"Error handling cookie banner: {e}")
        return False

def analyze_login_page():
    """Analyze Whydonate login page structure with cookie handling"""
    print("="*70)
    print("ANALYZING WHYDONATE LOGIN PAGE")
    print("="*70)
    
    # Setup Chrome with options
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Step 1: Go to Whydonate homepage
        print("\n1. Loading Whydonate homepage...")
        driver.get("https://www.whydonate.com")
        time.sleep(3)
        
        print(f"   Title: {driver.title}")
        print(f"   URL: {driver.current_url}")
        
        # Handle cookie banner on homepage
        print("\n2. Handling cookie banner...")
        cookie_handled = handle_cookie_banner(driver)
        
        if cookie_handled:
            print("   ✓ Cookie banner handled")
        else:
            print("   ⓘ No cookie banner or could not handle it")
        
        # Take screenshot after cookie handling
        driver.save_screenshot(str(BASE_DIR / "data" / "after_cookies.png"))
        print("   Screenshot saved: data/after_cookies.png")
        
        # Step 2: Navigate to login page
        print("\n3. Finding and clicking login link...")
        
        # Common login link selectors
        login_selectors = [
            "a[href*='/login']",
            "a:contains('Login')",
            "a:contains('Sign in')",
            "button:contains('Login')",
            "button:contains('Sign in')",
            "//a[contains(text(), 'Login')]",
            "//a[contains(text(), 'Sign in')]",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]"
        ]
        
        login_clicked = False
        for i, selector in enumerate(login_selectors):
            try:
                if selector.startswith("//"):
                    # XPath selector
                    elements = driver.find_elements(By.XPATH, selector)
                elif ":contains" in selector:
                    # Pseudo selector - convert to XPath
                    text = selector.split("'")[1]
                    elements = driver.find_elements(
                        By.XPATH, f"//{selector.split(':')[0]}[contains(text(), '{text}')]"
                    )
                else:
                    # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    element = elements[0]
                    print(f"   Found login element {i+1}: {selector}")
                    print(f"   Text: '{element.text}'")
                    
                    element.click()
                    login_clicked = True
                    print("   ✓ Clicked login link")
                    break
                    
            except Exception as e:
                continue
        
        if not login_clicked:
            print("   ✗ Could not find login link automatically")
            print("   Please navigate to login page manually in the browser")
            input("   Press Enter after navigating to login page...")
        else:
            time.sleep(3)  # Wait for login page to load
        
        # Step 3: Handle cookie banner on login page (if any)
        print("\n4. Checking for cookie banner on login page...")
        handle_cookie_banner(driver)
        
        # Step 4: Analyze login page
        print(f"\n5. Analyzing login page...")
        print(f"   Current URL: {driver.current_url}")
        print(f"   Page Title: {driver.title}")
        
        # Take screenshot of login page
        driver.save_screenshot(str(BASE_DIR / "data" / "login_page.png"))
        print("   Screenshot saved: data/login_page.png")
        
        # Save page source
        with open(BASE_DIR / "data" / "login_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   Page source saved: data/login_page_source.html")
        
        # Step 5: Analyze form structure
        print("\n" + "="*70)
        print("LOGIN FORM ANALYSIS")
        print("="*70)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} form(s) on page")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            form_id = form.get_attribute('id') or 'No ID'
            form_class = form.get_attribute('class') or 'No class'
            form_action = form.get_attribute('action') or 'No action'
            
            print(f"  ID: {form_id}")
            print(f"  Class: {form_class}")
            print(f"  Action: {form_action}")
            
            # Find all inputs in this form
            inputs = form.find_elements(By.TAG_NAME, "input")
            print(f"  Contains {len(inputs)} input(s):")
            
            for inp in inputs:
                inp_type = inp.get_attribute('type') or 'text'
                inp_name = inp.get_attribute('name') or 'No name'
                inp_id = inp.get_attribute('id') or 'No ID'
                inp_placeholder = inp.get_attribute('placeholder') or ''
                
                print(f"    - Type: {inp_type:<10} Name: {inp_name:<20} ID: {inp_id}")
                if inp_placeholder:
                    print(f"      Placeholder: '{inp_placeholder}'")
        
        # Step 6: Find email/password fields (search whole page)
        print("\n" + "="*70)
        print("EMAIL/PASSWORD FIELD SEARCH")
        print("="*70)
        
        # Find all input elements on page
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Total inputs on page: {len(all_inputs)}")
        
        email_candidates = []
        password_candidates = []
        
        for inp in all_inputs:
            inp_type = inp.get_attribute('type') or ''
            inp_name = inp.get_attribute('name') or ''
            inp_id = inp.get_attribute('id') or ''
            inp_placeholder = inp.get_attribute('placeholder') or ''
            
            # Check if this is an email field
            if (inp_type == 'email' or 
                'email' in inp_name.lower() or 
                'email' in inp_id.lower() or
                'e-mail' in inp_placeholder.lower() or
                'email' in inp_placeholder.lower()):
                email_candidates.append({
                    'element': inp,
                    'type': inp_type,
                    'name': inp_name,
                    'id': inp_id,
                    'placeholder': inp_placeholder
                })
            
            # Check if this is a password field
            if (inp_type == 'password' or 
                'password' in inp_name.lower() or 
                'password' in inp_id.lower() or
                'password' in inp_placeholder.lower()):
                password_candidates.append({
                    'element': inp,
                    'type': inp_type,
                    'name': inp_name,
                    'id': inp_id,
                    'placeholder': inp_placeholder
                })
        
        print(f"\nEmail field candidates ({len(email_candidates)}):")
        for i, cand in enumerate(email_candidates[:3]):  # Show first 3
            print(f"  {i+1}. Type: {cand['type']}, Name: '{cand['name']}', ID: '{cand['id']}'")
            if cand['placeholder']:
                print(f"     Placeholder: '{cand['placeholder']}'")
        
        print(f"\nPassword field candidates ({len(password_candidates)}):")
        for i, cand in enumerate(password_candidates[:3]):  # Show first 3
            print(f"  {i+1}. Type: {cand['type']}, Name: '{cand['name']}', ID: '{cand['id']}'")
            if cand['placeholder']:
                print(f"     Placeholder: '{cand['placeholder']}'")
        
        # Step 7: Find submit buttons
        print("\n" + "="*70)
        print("SUBMIT BUTTON SEARCH")
        print("="*70)
        
        # Look for submit buttons
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]",
            "//button[contains(text(), 'Log in')]",
            "button.btn-primary",
            "button.btn-login"
        ]
        
        submit_candidates = []
        
        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    submit_candidates.append({
                        'element': elem,
                        'selector': selector,
                        'text': elem.text,
                        'type': elem.get_attribute('type') or 'button'
                    })
            except:
                continue
        
        # Remove duplicates
        unique_candidates = []
        seen_elements = set()
        for cand in submit_candidates:
            elem_id = id(cand['element'])
            if elem_id not in seen_elements:
                seen_elements.add(elem_id)
                unique_candidates.append(cand)
        
        print(f"Found {len(unique_candidates)} unique submit button candidates:")
        for i, cand in enumerate(unique_candidates[:5]):  # Show first 5
            print(f"  {i+1}. Selector: {cand['selector']}")
            print(f"     Text: '{cand['text']}', Type: {cand['type']}")
        
        # Step 8: Create test login
        print("\n" + "="*70)
        print("TEST LOGIN ATTEMPT")
        print("="*70)
        
        if email_candidates and password_candidates and unique_candidates:
            print("Found all necessary elements. Testing login flow...")
            
            # Use first email field
            email_field = email_candidates[0]['element']
            email_field.clear()
            email_field.send_keys("test@example.com")
            print("  ✓ Entered test email")
            
            # Use first password field
            password_field = password_candidates[0]['element']
            password_field.clear()
            password_field.send_keys("testpassword")
            print("  ✓ Entered test password")
            
            # Use first submit button
            submit_button = unique_candidates[0]['element']
            print(f"  Clicking submit button: '{submit_button.text}'")
            
            # Take screenshot before submit
            driver.save_screenshot(str(BASE_DIR / "data" / "before_submit.png"))
            print("  Screenshot saved: data/before_submit.png")
            
            submit_button.click()
            time.sleep(3)
            
            # Take screenshot after submit
            driver.save_screenshot(str(BASE_DIR / "data" / "after_submit.png"))
            print("  Screenshot saved: data/after_submit.png")
            
            print(f"  Current URL after submit: {driver.current_url}")
            print(f"  Page title: {driver.title}")
            
            # Check if we got an error (expected with test credentials)
            error_selectors = [
                ".error", ".alert-danger", ".text-danger", 
                "[class*='error']", "[class*='Error']",
                "div[role='alert']"
            ]
            
            errors_found = []
            for selector in error_selectors:
                try:
                    errors = driver.find_elements(By.CSS_SELECTOR, selector)
                    for err in errors:
                        if err.text and err.text.strip():
                            errors_found.append(err.text.strip())
                except:
                    continue
            
            if errors_found:
                print(f"\n  Got error messages (expected with test credentials):")
                for err in errors_found[:2]:  # Show first 2 errors
                    print(f"    - {err[:100]}...")
            else:
                print("\n  No error messages found (unexpected)")
        
        else:
            print("Missing elements for test login:")
            if not email_candidates:
                print("  ✗ No email field found")
            if not password_candidates:
                print("  ✗ No password field found")
            if not unique_candidates:
                print("  ✗ No submit button found")
        
        # Step 9: Summary and recommendations
        print("\n" + "="*70)
        print("RECOMMENDED SELECTORS FOR BOT")
        print("="*70)
        
        print("\nBased on analysis, use these selectors:")
        
        if email_candidates:
            best_email = email_candidates[0]
            if best_email['name']:
                print(f"  Email field: By.NAME, '{best_email['name']}'")
            elif best_email['id']:
                print(f"  Email field: By.ID, '{best_email['id']}'")
            else:
                print(f"  Email field: By.XPATH, '//input[@type='email']'")
        
        if password_candidates:
            best_password = password_candidates[0]
            if best_password['name']:
                print(f"  Password field: By.NAME, '{best_password['name']}'")
            elif best_password['id']:
                print(f"  Password field: By.ID, '{best_password['id']}'")
            else:
                print(f"  Password field: By.XPATH, '//input[@type='password']'")
        
        if unique_candidates:
            best_submit = unique_candidates[0]
            print(f"  Submit button: {best_submit['selector']}")
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        
        print("\nCheck the screenshots in the 'data' folder for visual reference.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error screenshot
        try:
            driver.save_screenshot(str(BASE_DIR / "data" / "analysis_error.png"))
            print("Error screenshot saved: data/analysis_error.png")
        except:
            pass
    
    finally:
        print("\nBrowser will remain open for manual inspection...")
        print("Close the browser window when done, or press Enter here to close it.")
        input()
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    # Create data directory
    (BASE_DIR / "data").mkdir(exist_ok=True)
    
    analyze_login_page()

def handle_cookie_banner(self):
    """Handle cookie consent banner on Whydonate"""
    self.logger.info("Checking for cookie banner...")
    
    # Common cookie accept button texts (Dutch/English)
    accept_texts = [
        "Accept", "Accept All", "Accept Cookies", "I Accept", "Agree", 
        "Got it", "Okay", "OK", "Allow", "Consent", "Continue",
        "Accepteren", "Alles accepteren", "Cookies accepteren", "Akkoord",
        "Doorgaan", "Begrepen"
    ]
    
    # Common cookie banner selectors
    banner_selectors = [
        "div.cookie-banner",
        "div.cookie-notice", 
        "div[class*='cookie']",
        "div[class*='Cookie']",
        "div#cookie-banner",
        "div#cookie-notice",
        "div[data-testid='cookie-banner']",
        "div[role='alertdialog']",
        "div.consent-banner",
        "div.cookie-consent",
        "div#CybotCookiebotDialog"
    ]
    
    try:
        # Wait for banner to appear
        wait = WebDriverWait(self.driver, 5)
        
        for selector in banner_selectors:
            try:
                banner = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                self.logger.info(f"Found cookie banner with selector: {selector}")
                
                # Try different methods to find accept button
                accept_button = None
                
                # Method 1: Look for button with accept text
                for text in accept_texts:
                    try:
                        button = banner.find_element(
                            By.XPATH, f".//button[contains(text(), '{text}')]"
                        )
                        accept_button = button
                        self.logger.info(f"Found accept button with text: '{text}'")
                        break
                    except:
                        continue
                
                # Method 2: Look for button with data attribute
                if not accept_button:
                    try:
                        accept_button = banner.find_element(
                            By.CSS_SELECTOR, "button[data-testid='accept-cookies'], button[data-cy='accept-cookies']"
                        )
                        self.logger.info("Found accept button by data attribute")
                    except:
                        pass
                
                # Method 3: Look for any button in banner
                if not accept_button:
                    try:
                        buttons = banner.find_elements(By.TAG_NAME, "button")
                        if buttons:
                            accept_button = buttons[0]  # First button
                            self.logger.info(f"Using first button in banner: '{accept_button.text}'")
                    except:
                        pass
                
                if accept_button:
                    accept_button.click()
                    self.logger.info("Clicked accept button")
                    time.sleep(2)  # Wait for banner to disappear
                    return True
                else:
                    self.logger.warning("Could not find accept button in banner")
                    return False
                    
            except Exception as e:
                continue
        
        self.logger.info("No cookie banner found")
        return False
        
    except Exception as e:
        self.logger.warning(f"Error handling cookie banner: {e}")
        return False