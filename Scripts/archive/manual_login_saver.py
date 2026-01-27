from selenium import webdriver
import pickle
import time
import os

print("="*60)
print("MANUAL LOGIN HELPER")
print("="*60)
print("\nTHIS SCRIPT WILL:")
print("1. Open browser with your VPN")
print("2. YOU manually login (with space+backspace bug workaround)")
print("3. Save your session cookies")
print("4. Bot can reuse your session")
print("="*60)

# Create data directory
os.makedirs("data", exist_ok=True)

# Open browser
driver = webdriver.Chrome()

try:
    print("\n1. Opening Whydonate login page...")
    driver.get("https://whydonate.com/account/login")
    
    print("\n2. PLEASE DO THIS MANUALLY:")
    print("   a. Make sure VPN is connected (Netherlands)")
    print("   b. Click email field")
    print("   c. Type: gael.fichet@gmail.com")
    print("   d. Press SPACE then BACKSPACE (bug workaround)")
    print("   e. Type password: Whydonate@gael1")
    print("   f. Click login button")
    print("\n   Wait for login to complete...")
    
    input("\n3. Press Enter HERE after you've successfully logged in...")
    
    # Save cookies
    cookies = driver.get_cookies()
    
    with open("data/whydonate_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    print(f"\n✅ Saved {len(cookies)} cookies!")
    print("   Bot can now use your logged-in session.")
    
    # Test that we're logged in
    print(f"\n4. Verifying login status...")
    print(f"   Current URL: {driver.current_url}")
    print(f"   Page title: {driver.title}")
    
    if "login" not in driver.current_url:
        print("   ✅ Confirmed: Logged in!")
    else:
        print("   ⚠️  Warning: Still on login page")
    
    print("\n" + "="*60)
    print("MANUAL LOGIN COMPLETE")
    print("="*60)
    
    print("\nKeep browser open? (y/n)")
    keep_open = input().lower().strip()
    
    if keep_open != 'y':
        driver.quit()
        print("Browser closed.")
    else:
        print("Browser will stay open.")
        input("Press Enter when ready to close...")
        driver.quit()
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    driver.quit()

print("\nNext: Run the bot with saved cookies!")