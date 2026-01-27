from selenium import webdriver
import pickle
import json
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SESSION_DIR = BASE_DIR / "data" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

def save_complete_session(driver, session_name="whydonate"):
    """Save EVERYTHING needed to restore session"""
    print(f"\n💾 Saving complete session: {session_name}")
    
    session_data = {
        'cookies': driver.get_cookies(),
        'local_storage': {},
        'session_storage': {},
        'url': driver.current_url,
        'title': driver.title
    }
    
    # Save localStorage
    try:
        localStorage = driver.execute_script("""
            var items = {};
            for (var i = 0; i < localStorage.length; i++) {
                var key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        """)
        session_data['local_storage'] = localStorage
        print(f"   ✅ Saved {len(localStorage)} localStorage items")
    except:
        print("   ⚠️  Could not save localStorage")
    
    # Save sessionStorage
    try:
        sessionStorage = driver.execute_script("""
            var items = {};
            for (var i = 0; i < sessionStorage.length; i++) {
                var key = sessionStorage.key(i);
                items[key] = sessionStorage.getItem(key);
            }
            return items;
        """)
        session_data['session_storage'] = sessionStorage
        print(f"   ✅ Saved {len(sessionStorage)} sessionStorage items")
    except:
        print("   ⚠️  Could not save sessionStorage")
    
    # Save session data
    session_file = SESSION_DIR / f"{session_name}.pkl"
    with open(session_file, 'wb') as f:
        pickle.dump(session_data, f)
    
    print(f"   ✅ Session saved to: {session_file}")
    return session_file

def load_complete_session(driver, session_name="whydonate"):
    """Load EVERYTHING needed to restore session"""
    session_file = SESSION_DIR / f"{session_name}.pkl"
    
    if not session_file.exists():
        print(f"❌ No session file found: {session_file}")
        return False
    
    print(f"\n📂 Loading complete session: {session_name}")
    
    with open(session_file, 'rb') as f:
        session_data = pickle.load(f)
    
    # First navigate to the site
    driver.get("https://whydonate.com")
    time.sleep(2)
    
    # Clear existing cookies/storage
    driver.delete_all_cookies()
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    
    # Add cookies
    for cookie in session_data['cookies']:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    
    print(f"   ✅ Loaded {len(session_data['cookies'])} cookies")
    
    # Restore localStorage
    if session_data['local_storage']:
        try:
            for key, value in session_data['local_storage'].items():
                driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
            print(f"   ✅ Restored {len(session_data['local_storage'])} localStorage items")
        except:
            print("   ⚠️  Could not restore localStorage")
    
    # Restore sessionStorage
    if session_data['session_storage']:
        try:
            for key, value in session_data['session_storage'].items():
                driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")
            print(f"   ✅ Restored {len(session_data['session_storage'])} sessionStorage items")
        except:
            print("   ⚠️  Could not restore sessionStorage")
    
    # Refresh to apply everything
    driver.refresh()
    time.sleep(3)
    
    return True

def manual_login_and_save():
    """Manual login helper that saves complete session"""
    print("="*70)
    print("COMPLETE SESSION SAVER")
    print("="*70)
    print("\nFOLLOW THESE STEPS:")
    print("1. Make sure VPN is connected (Netherlands)")
    print("2. You'll manually login with the bug workaround")
    print("3. Everything will be saved for the bot")
    print("="*70)
    
    driver = webdriver.Chrome()
    
    try:
        # Step 1: Go to login
        print("\n1. Opening Whydonate login...")
        driver.get("https://whydonate.com/account/login")
        time.sleep(3)
        
        print("\n2. MANUALLY LOGIN NOW:")
        print("   Email: gael.fichet@gmail.com")
        print("   Bug: Type SPACE then BACKSPACE after email")
        print("   Password: Whydonate@gael1")
        print("   Click login button")
        
        input("\n3. Press Enter HERE after successful login...")
        
        # Step 2: Verify login
        current_url = driver.current_url
        print(f"\n   Current URL: {current_url}")
        print(f"   Page title: {driver.title}")
        
        if "login" in current_url:
            print("   ❌ Still on login page!")
            print("   Login may have failed.")
            return
        
        print("   ✅ Appears logged in!")
        
        # Step 3: Navigate to dashboard to ensure session is active
        print("\n4. Testing session...")
        driver.get("https://whydonate.com/en/dashboard")
        time.sleep(3)
        
        if "dashboard" in driver.current_url:
            print("   ✅ Dashboard accessible!")
        else:
            print(f"   ⚠️  May need different URL: {driver.current_url}")
        
        # Step 4: Save complete session
        save_complete_session(driver, "whydonate_full")
        
        # Step 5: Test restoring
        print("\n5. Testing session restore...")
        test_driver = webdriver.Chrome()
        
        if load_complete_session(test_driver, "whydonate_full"):
            test_driver.get("https://whydonate.com/en/dashboard")
            time.sleep(3)
            
            if "login" not in test_driver.current_url:
                print("   ✅ Session restore successful!")
                print("   Bot can use this session.")
            else:
                print("   ❌ Session restore failed")
                print("   Need different approach.")
            
            test_driver.quit()
        
        print("\n" + "="*70)
        print("SESSION SAVE COMPLETE")
        print("="*70)
        
        print("\nKeep original browser open? (y/n)")
        if input().lower().strip() != 'y':
            driver.quit()
        else:
            input("\nPress Enter to close browser...")
            driver.quit()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        driver.quit()

def bot_with_complete_session():
    """Bot that uses complete saved session"""
    print("="*70)
    print("BOT WITH COMPLETE SESSION")
    print("="*70)
    
    driver = webdriver.Chrome()
    
    try:
        # Load session
        if not load_complete_session(driver, "whydonate_full"):
            print("❌ Need to save session first!")
            print("Run: python complete_session_saver.py")
            return
        
        # Test if we're logged in
        print("\n🔍 Testing login status...")
        
        test_urls = [
            ("Dashboard", "https://whydonate.com/en/dashboard"),
            ("My Campaigns", "https://whydonate.com/en/my-campaigns"),
            ("Create Campaign", "https://whydonate.com/en/fundraiser/create")
        ]
        
        for name, url in test_urls:
            driver.get(url)
            time.sleep(2)
            
            if "login" not in driver.current_url:
                print(f"   ✅ {name}: Accessible")
            else:
                print(f"   ❌ {name}: Blocked (not logged in)")
        
        # If we can access create page, show it
        driver.get("https://whydonate.com/en/fundraiser/create")
        time.sleep(3)
        
        if "create" in driver.current_url:
            print("\n🎉 READY TO CREATE CAMPAIGNS!")
            print("The create form should be visible in browser.")
            
            # You can now automate form filling here
            # (We'll add that next)
        else:
            print(f"\n⚠️  Cannot access create page: {driver.current_url}")
        
        print("\n" + "="*70)
        print("BOT READY")
        print("="*70)
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Choose option:")
    print("1. Manual login and save session")
    print("2. Run bot with saved session")
    
    choice = input("\nSelect (1 or 2): ").strip()
    
    if choice == "1":
        manual_login_and_save()
    elif choice == "2":
        bot_with_complete_session()
    else:
        print("Invalid choice")