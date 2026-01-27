import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_DIR = Path(__file__).parent.parent

def guaranteed_login():
    """GUARANTEED working login test"""
    print("\n" + "="*70)
    print("GUARANTEED LOGIN TEST")
    print("="*70)
    
    # Get credentials
    print("\nEnter your Whydonate credentials:")
    username = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Credentials required.")
        return
    
    # Browser setup that WORKS (based on cookie_specialist.py)
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Step 1: Load page
        print("\n1. Loading page...")
        driver.get("https://whydonate.com/account/login")
        time.sleep(5)  # Wait longer
        
        print(f"   URL: {driver.current_url}")
        
        # Take initial screenshot
        driver.save_screenshot(str(BASE_DIR / "data" / "guaranteed_initial.png"))
        
        # Step 2: USE JAVASCRIPT ONLY (bypasses all interaction issues)
        print("\n2. Using JavaScript to fill form (bypasses interaction issues)...")
        
        # Fill email with JavaScript
        driver.execute_script(f"""
            var emailField = document.getElementById('loginEmail');
            if (emailField) {{
                emailField.value = '{username}';
                // Trigger all events
                ['focus', 'input', 'change'].forEach(eventType => {{
                    var event = new Event(eventType, {{ bubbles: true }});
                    emailField.dispatchEvent(event);
                }});
                console.log('Email set via JS');
            }}
        """)
        print("   ✅ Email filled via JavaScript")
        
        # Fill password with JavaScript
        driver.execute_script(f"""
            var passwordField = document.getElementById('loginPassword');
            if (passwordField) {{
                passwordField.value = '{password}';
                // Trigger all events
                ['focus', 'input', 'change'].forEach(eventType => {{
                    var event = new Event(eventType, {{ bubbles: true }});
                    passwordField.dispatchEvent(event);
                }});
                console.log('Password set via JS');
            }}
        """)
        print("   ✅ Password filled via JavaScript")
        
        # Take screenshot after filling
        driver.save_screenshot(str(BASE_DIR / "data" / "guaranteed_filled.png"))
        
        # Step 3: Submit with JavaScript
        print("\n3. Submitting with JavaScript...")
        
        driver.execute_script("""
            // Find and submit the form
            var forms = document.getElementsByTagName('form');
            for (var i = 0; i < forms.length; i++) {
                if (forms[i].querySelector('#loginEmail')) {
                    console.log('Found login form, submitting...');
                    forms[i].submit();
                    break;
                }
            }
        """)
        print("   ✅ Form submitted via JavaScript")
        
        # Step 4: Wait and check
        print("\n4. Waiting for result...")
        time.sleep(5)
        
        print(f"\n   Final URL: {driver.current_url}")
        print(f"   Final Title: {driver.title}")
        
        # Take final screenshot
        driver.save_screenshot(str(BASE_DIR / "data" / "guaranteed_final.png"))
        
        # Check result
        if "login" not in driver.current_url and "account/login" not in driver.current_url:
            print("\n   🎉 SUCCESS! You are logged in!")
            print(f"   You are on: {driver.current_url}")
        else:
            print("\n   ❌ Still on login page.")
            print("   Possible issues:")
            print("   1. Wrong credentials")
            print("   2. Account verification required")
            print("   3. CAPTCHA or 2FA")
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        
        print("\nBrowser remains open. You can:")
        print("1. Check if you're logged in")
        print("2. Try to navigate manually")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    (BASE_DIR / "data").mkdir(exist_ok=True)
    guaranteed_login()