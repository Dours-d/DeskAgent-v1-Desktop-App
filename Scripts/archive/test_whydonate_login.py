import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

def test_whydonate_manual():
    """Manual test of Whydonate login"""
    print("\n" + "="*60)
    print("Manual Whydonate Login Test")
    print("="*60)
    
    # Get credentials from user
    print("\nEnter your Whydonate credentials:")
    username = input("Email/Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("\nCredentials required for test.")
        return
    
    # Setup browser (visible for debugging)
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    print("\nLaunching browser...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Step 1: Go to Whydonate
        print("\n1. Navigating to Whydonate...")
        driver.get("https://www.whydonate.com")
        time.sleep(3)
        print(f"   Title: {driver.title}")
        
        # Step 2: Find and click login
        print("\n2. Looking for login link...")
        
        # Try different selectors for login link
        login_selectors = [
            "//a[contains(text(), 'Login')]",
            "//a[contains(text(), 'Sign in')]",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]",
            "//a[@href='/en/login']",
            "//a[@href*='login']"
        ]
        
        login_found = False
        for selector in login_selectors:
            try:
                login_elements = driver.find_elements(By.XPATH, selector)
                if login_elements:
                    login_element = login_elements[0]
                    print(f"   Found login with selector: {selector}")
                    print(f"   Text: {login_element.text}")
                    login_element.click()
                    login_found = True
                    break
            except:
                continue
        
        if not login_found:
            print("   Could not find login link. Please navigate manually.")
            print("   Current URL:", driver.current_url)
            input("   Press Enter after navigating to login page...")
        else:
            time.sleep(3)
        
        # Step 3: Fill login form
        print("\n3. Filling login form...")
        print(f"   Current URL: {driver.current_url}")
        
        # Find email field
        email_selectors = [
            "input[name='email']",
            "input[type='email']",
            "#email",
            "input[name='username']",
            "input[data-testid='email']"
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   Found email field with: {selector}")
                break
            except:
                continue
        
        if email_field:
            email_field.clear()
            email_field.send_keys(username)
            print("   ✓ Email entered")
        else:
            print("   ✗ Could not find email field")
            print("   Page source saved to email_field_debug.html")
            with open(BASE_DIR / "data" / "email_field_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        
        # Find password field
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "#password",
            "input[data-testid='password']"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   Found password field with: {selector}")
                break
            except:
                continue
        
        if password_field:
            password_field.clear()
            password_field.send_keys(password)
            print("   ✓ Password entered")
        else:
            print("   ✗ Could not find password field")
        
        # Step 4: Find and click submit button
        print("\n4. Looking for submit button...")
        
        submit_selectors = [
            "button[type='submit']",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]",
            "input[type='submit']",
            "button[data-testid='login-button']"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    submit_button = driver.find_element(By.XPATH, selector)
                else:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"   Found submit button with: {selector}")
                print(f"   Button text: {submit_button.text}")
                break
            except:
                continue
        
        if submit_button:
            # Take screenshot before clicking
            driver.save_screenshot(str(BASE_DIR / "data" / "before_login.png"))
            print("   Screenshot saved: before_login.png")
            
            submit_button.click()
            print("   ✓ Submit button clicked")
        else:
            print("   ✗ Could not find submit button")
            print("   Try pressing Enter manually in the browser...")
        
        # Step 5: Wait and check result
        print("\n5. Waiting for login result...")
        time.sleep(5)
        
        # Take screenshot after
        driver.save_screenshot(str(BASE_DIR / "data" / "after_login.png"))
        print("   Screenshot saved: after_login.png")
        
        # Check result
        current_url = driver.current_url
        print(f"\n6. Login Result:")
        print(f"   Current URL: {current_url}")
        print(f"   Page title: {driver.title}")
        
        success_indicators = ["/dashboard", "/my-campaigns", "/fundraiser", "account", "profile"]
        failed_indicators = ["/login", "error", "invalid", "incorrect"]
        
        success = any(indicator in current_url.lower() for indicator in success_indicators)
        failed = any(indicator in current_url.lower() for indicator in failed_indicators)
        
        if success:
            print("   ✅ LOGIN SUCCESSFUL!")
            
            # Check for welcome message
            try:
                welcome_elements = driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Hello') or contains(text(), 'Dashboard')]"
                )
                if welcome_elements:
                    for elem in welcome_elements[:2]:
                        if elem.text.strip():
                            print(f"   Welcome message: {elem.text[:100]}...")
            except:
                pass
                
        elif failed:
            print("   ❌ LOGIN FAILED!")
            
            # Look for error messages
            try:
                error_selectors = [
                    ".error", ".alert-danger", ".text-danger", 
                    "[class*='error']", "[class*='Error']",
                    "div[role='alert']", ".notification--error"
                ]
                
                for selector in error_selectors:
                    try:
                        errors = driver.find_elements(By.CSS_SELECTOR, selector)
                        for error in errors[:3]:
                            if error.text and error.text.strip():
                                print(f"   Error: {error.text[:200]}...")
                    except:
                        continue
            except:
                pass
        else:
            print("   ⚠️  Unknown result - check screenshots")
            
            # Save page source for debugging
            with open(BASE_DIR / "data" / "login_result.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("   Page source saved: login_result.html")
        
        print("\n" + "="*60)
        print("Test completed. Browser will remain open for inspection.")
        print("="*60)
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error screenshot
        try:
            driver.save_screenshot(str(BASE_DIR / "data" / "test_error.png"))
            print("Error screenshot saved: test_error.png")
        except:
            pass
        
        input("\nPress Enter to close browser...")
    
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    (BASE_DIR / "data").mkdir(exist_ok=True)
    
    test_whydonate_manual()