import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

BASE_DIR = Path(__file__).parent.parent

def simple_whydonate_login():
    """Simple test of Whydonate login"""
    print("\n" + "="*60)
    print("SIMPLE WHYDONATE LOGIN TEST")
    print("="*60)
    
    # Get credentials
    print("\nEnter your Whydonate credentials:")
    username = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Credentials required.")
        return
    
    # Setup browser
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Step 1: Go to login page
        print("\n1. Going to Whydonate login page...")
        driver.get("https://whydonate.com/account/login")
        time.sleep(3)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Take screenshot
        driver.save_screenshot(str(BASE_DIR / "data" / "login_page_simple.png"))
        print("   Screenshot saved: login_page_simple.png")
        
        # Step 2: Find email field
        print("\n2. Finding email field...")
        try:
            # Try by ID first (based on analysis)
            email_field = driver.find_element(By.ID, "loginEmail")
            print("   ✓ Found email field by ID: loginEmail")
        except:
            # Try by placeholder
            try:
                email_field = driver.find_element(
                    By.CSS_SELECTOR, "input[placeholder*='Email']"
                )
                print("   ✓ Found email field by placeholder")
            except:
                print("   ✗ Could not find email field")
                return
        
        # Step 3: Find password field
        print("\n3. Finding password field...")
        try:
            # Try by ID first
            password_field = driver.find_element(By.ID, "loginPassword")
            print("   ✓ Found password field by ID: loginPassword")
        except:
            # Try by placeholder
            try:
                password_field = driver.find_element(
                    By.CSS_SELECTOR, "input[placeholder*='Password']"
                )
                print("   ✓ Found password field by placeholder")
            except:
                print("   ✗ Could not find password field")
                return
        
        # Step 4: Enter credentials
        print("\n4. Entering credentials...")
        email_field.clear()
        email_field.send_keys(username)
        print("   ✓ Entered email")
        
        password_field.clear()
        password_field.send_keys(password)
        print("   ✓ Entered password")
        
        # Take screenshot before submit
        driver.save_screenshot(str(BASE_DIR / "data" / "before_login.png"))
        print("   Screenshot saved: before_login.png")
        
        # Step 5: Try to submit
        print("\n5. Submitting form...")
        
        # Method 1: Try to find submit button
        submit_button = None
        try:
            # Look for button with login text
            submit_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]"
            )
            print(f"   Found submit button: '{submit_button.text}'")
        except:
            # Try input type submit
            try:
                submit_button = driver.find_element(
                    By.CSS_SELECTOR, "input[type='submit'], button[type='submit']"
                )
                print(f"   Found submit button by type")
            except:
                print("   No submit button found, will try Enter key")
        
        if submit_button:
            submit_button.click()
            print("   ✓ Clicked submit button")
        else:
            # Press Enter key
            password_field.send_keys(Keys.RETURN)
            print("   ✓ Pressed Enter key")
        
        # Step 6: Wait and check result
        print("\n6. Waiting for login result...")
        time.sleep(5)
        
        # Take screenshot after
        driver.save_screenshot(str(BASE_DIR / "data" / "after_login.png"))
        print("   Screenshot saved: after_login.png")
        
        # Check result
        current_url = driver.current_url
        print(f"\n7. Login Result:")
        print(f"   Current URL: {current_url}")
        print(f"   Page title: {driver.title}")
        
        # Check for success
        if "/dashboard" in current_url or "/my-campaigns" in current_url:
            print("\n   ✅ LOGIN SUCCESSFUL!")
            print("   You are now logged into Whydonate.")
        elif "/account" in current_url and "login" not in current_url:
            print("\n   ✅ LOGIN SUCCESSFUL!")
            print("   You are in your account area.")
        elif "login" in current_url:
            print("\n   ❌ LOGIN FAILED!")
            print("   Still on login page.")
            
            # Check for errors
            try:
                error_elements = driver.find_elements(
                    By.CSS_SELECTOR, ".error, .text-danger, .invalid-feedback"
                )
                for err in error_elements:
                    if err.text:
                        print(f"   Error: {err.text[:100]}")
            except:
                pass
        else:
            print(f"\n   ⚠️  Unknown result")
            print(f"   You might be logged in. Check the browser.")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        
        print("\nBrowser will remain open. You can:")
        print("1. Check if you're logged in")
        print("2. Try navigating to: https://whydonate.com/en/fundraiser/create")
        print("3. Close the browser when done")
        
        input("\nPress Enter here to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    # Create data directory
    (BASE_DIR / "data").mkdir(exist_ok=True)
    
    simple_whydonate_login()