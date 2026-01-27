from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

print("="*60)
print("SIMULATE MANUAL LOGIN - TYPING CHARACTER BY CHARACTER")
print("="*60)

USERNAME = "gael.fichet@gmail.com"
PASSWORD = "Whydonate@gael1"

driver = webdriver.Chrome()

try:
    # Load page
    driver.get("https://whydonate.com/account/login")
    time.sleep(5)
    
    print("\nSimulating manual typing...")
    
    # Find elements
    email_field = driver.find_element(By.ID, "loginEmail")
    password_field = driver.find_element(By.ID, "loginPassword")
    
    # Click email field
    email_field.click()
    time.sleep(0.5)
    
    # Type email character by character (like human)
    print("Typing email...")
    for char in USERNAME:
        email_field.send_keys(char)
        time.sleep(0.05)  # Small delay between keystrokes
    
    time.sleep(0.5)
    
    # ADD THE SPACE BUG FIX
    print("Adding space (bug workaround)...")
    email_field.send_keys(" ")  # Add space
    time.sleep(0.3)
    
    print("Removing space...")
    email_field.send_keys(Keys.BACKSPACE)  # Remove space
    time.sleep(0.3)
    
    # Click password field
    password_field.click()
    time.sleep(0.5)
    
    # Type password character by character
    print("Typing password...")
    for char in PASSWORD:
        password_field.send_keys(char)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    # Submit
    print("Submitting...")
    password_field.send_keys(Keys.RETURN)
    
    # Wait for result
    time.sleep(5)
    
    print(f"\nResult:")
    print(f"URL: {driver.current_url}")
    print(f"Title: {driver.title}")
    
    if "login" not in driver.current_url:
        print("\n🎉 SUCCESS! Bug workaround worked!")
    else:
        print("\n❌ Still on login page")
        
        # Try one more thing - click submit button
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(3)
            
            print(f"After button click:")
            print(f"URL: {driver.current_url}")
        except:
            print("Could not find submit button")
    
    input("\nPress Enter to close browser...")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()