import os
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

BASE_DIR = Path(__file__).parent.parent
PROFILE_DIR = BASE_DIR / "data" / "chrome_profile"

def setup_profile_based_bot():
    """Setup bot that uses persistent Chrome profile"""
    print("="*70)
    print("PERSISTENT PROFILE BOT")
    print("="*70)
    
    # Create profile directory
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    options = Options()
    
    # Use persistent profile
    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    options.add_argument("profile-directory=Default")
    
    # Keep browser open
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options)
    
    print(f"\n📁 Using profile: {PROFILE_DIR}")
    print("\nINSTRUCTIONS:")
    print("1. Browser will open with fresh profile")
    print("2. MANUALLY: Connect VPN")
    print("3. MANUALLY: Login to Whydonate with bug workaround")
    print("4. Close browser when done")
    print("5. Next time, bot will reuse your logged-in profile")
    print("="*70)
    
    # First visit
    driver.get("https://whydonate.com/account/login")
    
    input("\nPress Enter after you've manually logged in and closed browser...")
    
    print(f"\n✅ Profile saved. Next time bot will be logged in!")

def run_profile_bot():
    """Run bot with persistent profile"""
    if not PROFILE_DIR.exists():
        print("❌ No profile found. Run setup first.")
        return
    
    print("\n🚀 Starting bot with persistent profile...")
    
    options = Options()
    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    options.add_argument("profile-directory=Default")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Should already be logged in
        driver.get("https://whydonate.com/en/dashboard")
        time.sleep(3)
        
        if "login" not in driver.current_url:
            print("✅ Already logged in via profile!")
            
            # Test campaign creation
            driver.get("https://whydonate.com/en/fundraiser/create")
            time.sleep(3)
            
            if "create" in driver.current_url:
                print("🎉 Ready to automate campaign creation!")
                print("\nThe create form is open in browser.")
                print("You can now add automation to fill the form.")
            else:
                print(f"⚠️  Cannot access create: {driver.current_url}")
        else:
            print("❌ Not logged in. Profile may need setup.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to close...")

if __name__ == "__main__":
    print("Choose:")
    print("1. Setup persistent profile (manual login once)")
    print("2. Run bot with profile")
    
    choice = input("\nSelect: ").strip()
    
    if choice == "1":
        setup_profile_based_bot()
    elif choice == "2":
        run_profile_bot()