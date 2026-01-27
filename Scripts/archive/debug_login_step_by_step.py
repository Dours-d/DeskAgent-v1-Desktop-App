from selenium import webdriver
import time

print("="*60)
print("DEBUG LOGIN - STEP BY STEP")
print("="*60)

USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

driver = webdriver.Chrome()

try:
    # Step 1: Load page
    print("\n1. Loading login page...")
    driver.get("https://whydonate.com/account/login")
    time.sleep(5)
    
    print(f"   URL: {driver.current_url}")
    print(f"   Title: {driver.title}")
    
    # Take screenshot
    driver.save_screenshot("debug_step1.png")
    
    # Step 2: Check what's on the page
    print("\n2. Analyzing page...")
    
    # Get page source and check for elements
    page_source = driver.page_source
    
    # Check if email field exists
    if 'loginEmail' in page_source:
        print("   ✅ loginEmail field found in HTML")
    else:
        print("   ❌ loginEmail field NOT FOUND in HTML")
    
    # Check if password field exists  
    if 'loginPassword' in page_source:
        print("   ✅ loginPassword field found in HTML")
    else:
        print("   ❌ loginPassword field NOT FOUND in HTML")
    
    # Check for form
    if '<form' in page_source:
        print("   ✅ Form tag found")
    else:
        print("   ❌ No form tag found")
    
    # Step 3: Try JavaScript to see elements
    print("\n3. Checking elements with JavaScript...")
    
    # Check email field
    email_exists = driver.execute_script("""
        var email = document.getElementById('loginEmail');
        if (email) {
            console.log('Email field found');
            return {
                exists: true,
                value: email.value,
                type: email.type,
                disabled: email.disabled,
                readOnly: email.readOnly
            };
        }
        return { exists: false };
    """)
    
    if email_exists.get('exists'):
        print(f"   ✅ Email field exists")
        print(f"     Current value: '{email_exists.get('value')}'")
        print(f"     Type: {email_exists.get('type')}")
        print(f"     Disabled: {email_exists.get('disabled')}")
        print(f"     Readonly: {email_exists.get('readOnly')}")
    else:
        print("   ❌ Email field not found via JavaScript")
    
    # Check password field
    password_exists = driver.execute_script("""
        var password = document.getElementById('loginPassword');
        if (password) {
            console.log('Password field found');
            return {
                exists: true,
                value: password.value,
                type: password.type,
                disabled: password.disabled,
                readOnly: password.readOnly
            };
        }
        return { exists: false };
    """)
    
    if password_exists.get('exists'):
        print(f"   ✅ Password field exists")
        print(f"     Current value: '{password_exists.get('value')}'")
        print(f"     Type: {password_exists.get('type')}")
        print(f"     Disabled: {password_exists.get('disabled')}")
        print(f"     Readonly: {password_exists.get('readOnly')}")
    else:
        print("   ❌ Password field not found via JavaScript")
    
    # Step 4: Try the bug workaround
    print("\n4. Trying bug workaround...")
    
    # Set email with space workaround
    result = driver.execute_script(f"""
        var email = document.getElementById('loginEmail');
        if (email) {{
            // Set value
            email.value = '{USERNAME}';
            
            // Add space
            email.value = email.value + ' ';
            
            // Trigger input event
            var inputEvent = new Event('input', {{ bubbles: true }});
            email.dispatchEvent(inputEvent);
            
            // Remove space
            email.value = email.value.trim();
            
            // Trigger events again
            email.dispatchEvent(new Event('input', {{ bubbles: true }}));
            email.dispatchEvent(new Event('change', {{ bubbles: true }}));
            email.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            
            console.log('Bug workaround applied');
            return 'SUCCESS';
        }}
        return 'FAILED - no email field';
    """)
    
    print(f"   Bug workaround result: {result}")
    
    # Set password
    result2 = driver.execute_script(f"""
        var password = document.getElementById('loginPassword');
        if (password) {{
            password.value = '{PASSWORD}';
            
            // Trigger all events
            ['input', 'change', 'blur'].forEach(eventType => {{
                password.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
            }});
            
            console.log('Password set');
            return 'SUCCESS';
        }}
        return 'FAILED - no password field';
    """)
    
    print(f"   Password set result: {result2}")
    
    # Step 5: Check form validation state
    print("\n5. Checking form validation...")
    
    validation = driver.execute_script("""
        var form = document.querySelector('form');
        if (form) {
            return {
                formExists: true,
                checkValidity: form.checkValidity(),
                elements: form.elements.length
            };
        }
        return { formExists: false };
    """)
    
    if validation.get('formExists'):
        print(f"   ✅ Form found with {validation.get('elements')} elements")
        print(f"   Form valid: {validation.get('checkValidity')}")
    else:
        print("   ❌ No form found")
    
    # Step 6: Try to submit and see what happens
    print("\n6. Attempting submit...")
    
    submit_result = driver.execute_script("""
        var form = document.querySelector('form');
        if (form) {
            try {
                form.submit();
                return 'Form submitted';
            } catch(e) {
                return 'Submit error: ' + e.message;
            }
        }
        return 'No form to submit';
    """)
    
    print(f"   Submit result: {submit_result}")
    
    # Step 7: Wait and check
    time.sleep(3)
    
    print(f"\n7. After submit attempt:")
    print(f"   URL: {driver.current_url}")
    print(f"   Title: {driver.title}")
    
    # Check for any error messages
    errors = driver.execute_script("""
        var errors = [];
        // Look for error elements
        var errorSelectors = ['.error', '.text-danger', '.invalid-feedback', '[class*="error"]'];
        
        errorSelectors.forEach(selector => {
            var elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el.textContent && el.textContent.trim()) {
                    errors.push(el.textContent.trim());
                }
            });
        });
        
        return errors;
    """)
    
    if errors:
        print(f"\n   Error messages found:")
        for err in errors[:3]:  # Show first 3 errors
            print(f"   - {err}")
    else:
        print(f"\n   No error messages found")
    
    print("\n" + "="*60)
    print("DEBUG COMPLETE")
    print("="*60)
    
    print("\nBrowser will stay open. You can:")
    print("1. Check the Console (F12 → Console tab)")
    print("2. See if there are JavaScript errors")
    print("3. Check Network tab for failed requests")
    
    input("\nPress Enter to close browser...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()
    print("\nBrowser closed.")
    