from selenium import webdriver
import pickle
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class CookieBot:
    def __init__(self):
        self.cookie_file = BASE_DIR / "data" / "whydonate_cookies.pkl"
        
    def load_cookies(self):
        """Load saved cookies and check login status"""
        if not self.cookie_file.exists():
            print("❌ No saved cookies found!")
            print("Run manual_login_saver.py first")
            return None
        
        driver = webdriver.Chrome()
        
        try:
            # First visit the site
            driver.get("https://whydonate.com")
            time.sleep(2)
            
            # Load cookies
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass  # Skip invalid cookies
            
            print(f"✅ Loaded {len(cookies)} cookies")
            
            # Refresh to apply cookies
            driver.refresh()
            time.sleep(3)
            
            return driver
            
        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            driver.quit()
            return None
    
    def check_login(self, driver):
        """Check if we're logged in"""
        # Try to access a protected page
        driver.get("https://whydonate.com/en/dashboard")
        time.sleep(3)
        
        if "login" not in driver.current_url:
            print("✅ Confirmed: Logged in with cookies!")
            return True
        else:
            print("❌ Not logged in - cookies may have expired")
            return False
    
    def create_campaign(self, campaign_data):
        """Create a campaign using logged-in session"""
        driver = self.load_cookies()
        
        if not driver:
            return False
        
        try:
            # Check login first
            if not self.check_login(driver):
                return False
            
            print("\n📝 Creating campaign...")
            
            # Navigate to create page
            create_urls = [
                "https://whydonate.com/en/fundraiser/create",
                "https://whydonate.com/fundraiser/create"
            ]
            
            for url in create_urls:
                driver.get(url)
                time.sleep(3)
                
                if "create" in driver.current_url:
                    print(f"✅ Found create page: {driver.current_url}")
                    break
            
            # Take screenshot
            driver.save_screenshot("create_page.png")
            
            # Fill form (simplified for now)
            print("\nCampaign creation page loaded!")
            print("You can see the form in the browser.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        finally:
            print("\nBrowser will stay open...")
            input("Press Enter to close...")
            driver.quit()

def main():
    print("="*60)
    print("WHYDONATE BOT WITH SAVED COOKIES")
    print("="*60)
    
    bot = CookieBot()
    
    print("\n1. Checking saved session...")
    driver = bot.load_cookies()
    
    if driver:
        print("\n2. Testing login status...")
        if bot.check_login(driver):
            print("\n3. Ready to create campaigns!")
            
            # Test campaign creation
            test_data = {
                "title": "Test Campaign",
                "description": "Test description",
                "target": 1000
            }
            
            bot.create_campaign(test_data)
        else:
            print("\n❌ Session expired. Run manual_login_saver.py again.")
    else:
        print("\n❌ No valid session. Run manual_login_saver.py first.")

if __name__ == "__main__":
    main()