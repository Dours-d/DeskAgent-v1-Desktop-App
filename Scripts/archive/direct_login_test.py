from selenium import webdriver
from selenium.webdriver.common.by import By
import time

print("="*60)
print("DIRECT LOGIN TEST")
print("="*60)

# Your credentials (hardcoded for testing)
USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

print(f"\nTesting login for: {USERNAME}")
print("Browser will open and attempt to login...")

driver = webdriver.Chrome()

try:
    # 1. Go to login page
    print("\n1. Loading login page...")
    driver.get("https://whydonate.com/account/login")
    time.sleep(5)  # Give plenty of time
    
    print(f"   Title: {driver.title}")
    
    # 2. Use JavaScript to fill and submit (bypasses interaction issues)
    print("\n2. Filling form with JavaScript...")
    
    # Fill email
    driver.execute_script(f"""
        var email = document.getElementById('loginEmail');
        if (email) {{
            email.value = '{USERNAME}';
            console.log('Email filled');
        }}
    """)
    
    # Fill password  
    driver.execute_script(f"""
        var password = document.getElementById('loginPassword');
        if (password) {{
            password.value = '{PASSWORD}';
            console.log('Password filled');
        }}
    """)
    
    # Submit form
    driver.execute_script("""
        var form = document.querySelector('form');
        if (form) {
            form.submit();
            console.log('Form submitted');
        }
    """)
    
    print("   ✅ Form submitted via JavaScript")
    
    # 3. Wait and check result
    print("\n3. Waiting for login result...")
    time.sleep(5)
    
    current_url = driver.current_url
    print(f"\n   Current URL: {current_url}")
    print(f"   Page title: {driver.title}")
    
    # 4. Check if login succeeded
    if "login" not in current_url and "account/login" not in current_url:
        print("\n   🎉 LOGIN SUCCESSFUL!")
        print(f"   You are now at: {current_url}")
        
        # Save screenshot
        driver.save_screenshot("login_success.png")
        print("   Screenshot saved: login_success.png")
    else:
        print("\n   ❌ LOGIN FAILED - Still on login page")
        
        # Check for error messages
        page_html = driver.page_source
        if "invalid" in page_html.lower() or "incorrect" in page_html.lower():
            print("   ⚠️  Error: Invalid email or password")
        elif "verify" in page_html.lower():
            print("   ⚠️  Error: Account needs verification")
        
        # Save screenshot of error
        driver.save_screenshot("login_failed.png")
        print("   Screenshot saved: login_failed.png")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    print("\nBrowser remains open. You can:")
    print("1. Check the URL to confirm login status")
    print("2. Try to navigate manually")
    
    input("\nPress Enter to close browser...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()
    print("\nBrowser closed.")