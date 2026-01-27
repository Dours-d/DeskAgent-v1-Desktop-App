from selenium.webdriver.common.by import By
import time

print("Quick cookie banner test...")
print("Opening browser to Whydonate login page...")

driver = webdriver.Chrome()
driver.get("https://whydonate.com/account/login")
time.sleep(5)

print(f"\nPage loaded:")
print(f"URL: {driver.current_url}")
print(f"Title: {driver.title}")

# Take screenshot
driver.save_screenshot("cookie_test.png")
print("Screenshot saved: cookie_test.png")

# Look for the CybotCookiebotDialog (very common)
print("\nLooking for Cookiebot dialog...")
try:
    cookiebot = driver.find_element(By.ID, "CybotCookiebotDialog")
    print("✅ FOUND Cookiebot dialog!")
    print(f"Displayed: {cookiebot.is_displayed()}")
    
    # Look for accept button
    try:
        accept_button = cookiebot.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        print(f"Found accept button: '{accept_button.text}'")
        
        if accept_button.is_displayed() and accept_button.is_enabled():
            print("Clicking accept button...")
            accept_button.click()
            time.sleep(2)
            print("✅ Clicked!")
        else:
            print("Button not clickable")
            
    except Exception as e:
        print(f"No accept button found: {e}")
        
        # Try other buttons
        buttons = cookiebot.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons in dialog")
        for btn in buttons:
            print(f"  Button: '{btn.text}'")
            
except:
    print("❌ No Cookiebot dialog found")

print("\nNow trying to interact with login form...")

# Try to click email field
try:
    email_field = driver.find_element(By.ID, "loginEmail")
    print(f"\nEmail field found")
    print(f"Displayed: {email_field.is_displayed()}")
    print(f"Enabled: {email_field.is_enabled()}")
    
    # Try to click
    try:
        email_field.click()
        print("✅ Can click email field")
    except:
        print("❌ Cannot click email field")
        
except:
    print("❌ Cannot find email field")

print("\nBrowser will stay open. Check if:")
print("1. Cookie banner is visible (usually at bottom)")
print("2. You can click the 'Accept' button manually")
print("3. After accepting, you can click the email field")

input("\nPress Enter to close browser...")
driver.quit()