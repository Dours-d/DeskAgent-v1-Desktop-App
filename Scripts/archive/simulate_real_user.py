from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random

print("="*60)
print("SIMULATE REAL USER BEHAVIOR")
print("="*60)

USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

driver = webdriver.Chrome()

try:
    # Load page with human-like delay
    print("Opening browser...")
    time.sleep(random.uniform(1, 2))
    
    driver.get("https://whydonate.com/account/login")
    time.sleep(random.uniform(3, 5))  # Human reading time
    
    print(f"Page loaded: {driver.title}")
    
    # Find elements
    email_field = driver.find_element(By.ID, "loginEmail")
    password_field = driver.find_element(By.ID, "loginPassword")
    
    # Human-like interaction with email
    print("\nTyping email (human speed)...")
    actions = ActionChains(driver)
    
    # Click email field
    actions.move_to_element(email_field).pause(random.uniform(0.5, 1)).click().perform()
    time.sleep(random.uniform(0.2, 0.5))
    
    # Type email with human-like delays
    for char in USERNAME:
        actions.send_keys(char).pause(random.uniform(0.05, 0.15))
    actions.perform()
    
    time.sleep(random.uniform(0.3, 0.7))
    
    # Apply the bug workaround manually
    print("Applying bug workaround (space then backspace)...")
    actions.send_keys(" ").pause(0.3).send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.5)
    
    # Tab to password field (like a human would)
    print("\nMoving to password field...")
    actions.send_keys(Keys.TAB).perform()
    time.sleep(random.uniform(0.3, 0.7))
    
    # Type password
    print("Typing password...")
    for char in PASSWORD:
        actions.send_keys(char).pause(random.uniform(0.05, 0.15))
    actions.perform()
    
    time.sleep(random.uniform(0.5, 1))
    
    # Look for submit button
    print("\nLooking for submit button...")
    
    # Try common submit button locations
    try:
        # First try: button with type submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print(f"Found submit button: '{submit_button.text}'")
        
    except:
        try:
            # Second try: any button with login text
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]")
            print(f"Found login button: '{submit_button.text}'")
            
        except:
            try:
                # Third try: input type submit
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                print(f"Found submit input")
                
            except:
                print("No submit button found, trying Enter key...")
                actions.send_keys(Keys.RETURN).perform()
                submit_button = None
    
    # Click submit button if found
    if submit_button:
        print("Clicking submit button...")
        
        # Move to button and click (human-like)
        actions.move_to_element(submit_button).pause(random.uniform(0.3, 0.7)).click().perform()
    
    # Wait for result
    print("\nWaiting for login...")
    time.sleep(5)
    
    # Check result
    current_url = driver.current_url
    print(f"\nResult URL: {current_url}")
    print(f"Page title: {driver.title}")
    
    if "login" not in current_url:
        print("\n🎉 SUCCESS! Login worked with real user simulation!")
    else:
        print("\n❌ Still on login page")
        
        # Save page for debugging
        with open("failed_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page saved as: failed_login.html")
    
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