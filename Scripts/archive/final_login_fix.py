from selenium import webdriver
from selenium.webdriver.common.by import By
import time

print("="*60)
print("FINAL LOGIN FIX - CLICK SUBMIT BUTTON")
print("="*60)

USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

driver = webdriver.Chrome()

try:
    # Load page
    print("\n1. Loading page...")
    driver.get("https://whydonate.com/account/login")
    time.sleep(5)
    
    # Apply bug workaround and fill form
    print("\n2. Filling form with bug workaround...")
    
    driver.execute_script(f"""
        // Fill email with space workaround
        var email = document.getElementById('loginEmail');
        if (email) {{
            email.value = '{USERNAME} ';
            email.dispatchEvent(new Event('input', {{ bubbles: true }}));
            
            setTimeout(function() {{
                email.value = email.value.trim();
                email.dispatchEvent(new Event('input', {{ bubbles: true }}));
                email.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}, 100);
        }}
        
        // Fill password
        var password = document.getElementById('loginPassword');
        if (password) {{
            password.value = '{PASSWORD}';
            password.dispatchEvent(new Event('input', {{ bubbles: true }}));
            password.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    """)
    
    time.sleep(1)
    
    # Find and click the REAL submit button
    print("\n3. Looking for submit button...")
    
    # Try to find submit button by various methods
    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "//button[contains(text(), 'Login')]",
        "//button[contains(text(), 'Sign in')]",
        "//button[contains(text(), 'Inloggen')]",  # Dutch
        ".btn-primary",
        "[data-testid='login-button']"
    ]
    
    button_found = False
    
    for selector in submit_selectors:
        try:
            if selector.startswith("//"):
                elements = driver.find_elements(By.XPATH, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    print(f"   ✅ Found submit button: '{element.text}'")
                    print(f"   Clicking button...")
                    
                    # Click with JavaScript (more reliable)
                    driver.execute_script("arguments[0].click();", element)
                    button_found = True
                    break
            
            if button_found:
                break
                
        except Exception as e:
            continue
    
    if not button_found:
        print("   ❌ No submit button found, trying alternative...")
        
        # Try to trigger form submission via button click event
        driver.execute_script("""
            // Find any button in the form and click it
            var form = document.querySelector('form');
            if (form) {
                var buttons = form.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].offsetParent !== null) { // Is visible
                        buttons[i].click();
                        console.log('Clicked form button');
                        break;
                    }
                }
            }
        """)
    
    # Wait for result
    print("\n4. Waiting for login result...")
    time.sleep(5)
    
    print(f"\n   Current URL: {driver.current_url}")
    print(f"   Page title: {driver.title}")
    
    # Check result
    if "login" not in driver.current_url and "account/login" not in driver.current_url:
        print("\n   🎉 LOGIN SUCCESSFUL!")
        
        # Save cookies for future use
        import pickle
        cookies = driver.get_cookies()
        with open("whydonate_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
        print("   ✅ Cookies saved for future sessions")
        
    else:
        print("\n   ❌ Still on login page")
        
        # Check for hidden error messages
        page_html = driver.page_source.lower()
        if "invalid" in page_html or "incorrect" in page_html:
            print("   ⚠️  Invalid credentials")
        elif "required" in page_html:
            print("   ⚠️  Required field missing")
        
        # Check console for JavaScript errors
        print("\n   Checking browser console for errors...")
        logs = driver.get_log('browser')
        if logs:
            print("   JavaScript console errors:")
            for log in logs[:3]:  # Show first 3 errors
                print(f"   - {log.get('message', '')[:100]}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    input("\nPress Enter to close browser...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()
    print("\nBrowser closed.")