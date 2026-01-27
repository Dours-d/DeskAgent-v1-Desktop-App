from selenium import webdriver
from selenium.webdriver.common.by import By
import time

print("="*60)
print("FIXED LOGIN - WITH WHYDONATE BUG WORKAROUND")
print("="*60)

# Your credentials
USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

print(f"\nTesting login with bug workaround for: {USERNAME}")

driver = webdriver.Chrome()

try:
    # 1. Go to login page
    print("\n1. Loading login page...")
    driver.get("https://whydonate.com/account/login")
    time.sleep(5)
    
    print(f"   Title: {driver.title}")
    
    # 2. FIX THE BUG: Add space then erase it
    print("\n2. Applying Whydonate bug workaround...")
    
    # Step 1: Fill email
    driver.execute_script(f"""
        var email = document.getElementById('loginEmail');
        if (email) {{
            email.value = '{USERNAME}';
            console.log('Email filled');
            
            // TRIGGER THE BUG FIX: Add space then erase
            setTimeout(function() {{
                email.value = email.value + ' ';
                email.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                setTimeout(function() {{
                    email.value = email.value.trim();
                    email.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    email.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    console.log('Bug workaround applied');
                }}, 100);
            }}, 100);
        }}
    """)
    
    time.sleep(1)  # Wait for bug workaround
    
    # Step 2: Fill password
    driver.execute_script(f"""
        var password = document.getElementById('loginPassword');
        if (password) {{
            password.value = '{PASSWORD}';
            console.log('Password filled');
            
            // Also trigger events for password
            password.dispatchEvent(new Event('input', {{ bubbles: true }}));
            password.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    """)
    
    time.sleep(1)
    
    # Step 3: Submit form
    print("\n3. Submitting form...")
    driver.execute_script("""
        // Find the form and submit
        var forms = document.getElementsByTagName('form');
        for (var i = 0; i < forms.length; i++) {
            if (forms[i].querySelector('#loginEmail')) {
                console.log('Submitting form...');
                forms[i].submit();
                break;
            }
        }
    """)
    
    print("   ✅ Form submitted with bug workaround")
    
    # 4. Wait and check
    print("\n4. Waiting for login result...")
    time.sleep(5)
    
    current_url = driver.current_url
    print(f"\n   Current URL: {current_url}")
    print(f"   Page title: {driver.title}")
    
    # 5. Check result
    if "login" not in current_url and "account/login" not in current_url:
        print("\n   🎉 LOGIN SUCCESSFUL WITH BUG WORKAROUND!")
        print(f"   You are now at: {current_url}")
        
        # Save screenshot
        driver.save_screenshot("login_success_fixed.png")
        print("   Screenshot saved: login_success_fixed.png")
    else:
        print("\n   ❌ Still failed")
        
        # Show page content for debugging
        page_html = driver.page_source.lower()
        if "invalid" in page_html:
            print("   ⚠️  Still getting 'invalid credentials'")
        elif "verify" in page_html:
            print("   ⚠️  Needs account verification")
        
        driver.save_screenshot("login_still_failed.png")
        print("   Screenshot saved: login_still_failed.png")
    
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