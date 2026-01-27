import sys
from pathlib import Path
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path(__file__).parent.parent

class VPNWhydonateBot:
    """Whydonate bot with VPN/geo awareness"""
    
    def __init__(self, vpn_required=True):
        self.base_dir = BASE_DIR
        self.vpn_required = vpn_required
        
        print(f"\n🔧 Initializing VPN-Aware Whydonate Bot")
        print(f"   VPN Required: {vpn_required}")
        
        self.check_environment()
        self.driver = self.setup_browser_with_vpn_settings()
        
    def check_environment(self):
        """Check if VPN is properly configured"""
        print("\n🌍 Checking environment...")
        
        # Load location if exists
        location_file = self.base_dir / "data" / "location.json"
        if location_file.exists():
            try:
                with open(location_file, 'r') as f:
                    location = json.load(f)
                
                country = location.get('country_code', 'Unknown')
                print(f"   Detected location: {country}")
                
                if self.vpn_required and country != 'NL':
                    print(f"\n⚠️  WARNING: Not in Netherlands ({country})")
                    print("   Whydonate may block access.")
                    print("   Consider connecting to VPN in Netherlands.")
                    
                    response = input("\n   Continue anyway? (y/n): ").lower()
                    if response != 'y':
                        print("   Exiting...")
                        sys.exit(0)
                        
            except:
                print("   Could not read location data")
        else:
            print("   No location data found")
    
    def setup_browser_with_vpn_settings(self):
        """Setup browser with VPN/anti-blocking settings"""
        print("\n⚙️  Setting up browser with VPN/anti-blocking settings...")
        
        options = webdriver.ChromeOptions()
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # VPN/Geo settings
        options.add_argument('--lang=en-US,en;q=0.9')
        options.add_argument('--timezone=Europe/Amsterdam')
        
        # Make browser look more human
        options.add_argument('--window-size=1200,800')
        options.add_argument('--disable-notifications')
        
        # Disable save password prompt
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=options)
        
        # Execute anti-detection scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("   ✅ Browser configured for VPN/geo access")
        return driver
    
    def clear_browser_data(self):
        """Clear cookies and cache (important for Whydonate)"""
        print("\n🧹 Clearing browser data...")
        
        # Navigate to blank page first
        self.driver.get("about:blank")
        time.sleep(1)
        
        # Clear cookies
        self.driver.delete_all_cookies()
        print("   ✅ Cookies cleared")
        
        # Clear localStorage and sessionStorage via JavaScript
        self.driver.execute_script("""
            try {
                localStorage.clear();
                sessionStorage.clear();
                console.log('Browser storage cleared');
            } catch(e) {
                console.log('Could not clear storage:', e);
            }
        """)
        
        time.sleep(1)
    
    def login_with_retry(self, username, password, max_retries=3):
        """Login with retry logic for geo-blocked sites"""
        print(f"\n🔐 Attempting login (max {max_retries} retries)...")
        
        for attempt in range(1, max_retries + 1):
            print(f"\n   Attempt {attempt}/{max_retries}")
            
            try:
                # Clear data before each attempt
                self.clear_browser_data()
                
                # Load login page
                print("   Loading login page...")
                self.driver.get("https://whydonate.com/account/login")
                time.sleep(5)  # Wait for geo-checks
                
                # Check if we got a blocked page
                current_url = self.driver.current_url.lower()
                if "blocked" in current_url or "access denied" in self.driver.title.lower():
                    print(f"   ❌ Page blocked (geo restriction)")
                    
                    if attempt < max_retries:
                        print("   Waiting 10 seconds before retry...")
                        time.sleep(10)
                        continue
                    else:
                        print("   ⚠️  Max retries reached")
                        return False
                
                # Use JavaScript to login (bypasses interaction issues)
                print("   Using JavaScript login...")
                
                success = self.javascript_login(username, password)
                
                if success:
                    print(f"   ✅ Login successful on attempt {attempt}")
                    return True
                else:
                    print(f"   ❌ Login failed")
                    
                    if attempt < max_retries:
                        print("   Waiting 5 seconds before retry...")
                        time.sleep(5)
            
            except Exception as e:
                print(f"   ❌ Error on attempt {attempt}: {e}")
                
                if attempt < max_retries:
                    print("   Waiting 5 seconds before retry...")
                    time.sleep(5)
        
        print("\n   ⚠️  All login attempts failed")
        return False
    
    def javascript_login(self, username, password):
        """Login using only JavaScript (bypasses all interaction issues)"""
        try:
            # Fill form with JavaScript
            self.driver.execute_script(f"""
                // Fill email
                var emailField = document.getElementById('loginEmail');
                if (emailField) {{
                    emailField.value = '{username}';
                    ['focus', 'input', 'change'].forEach(eventType => {{
                        emailField.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
                    }});
                }}
                
                // Fill password
                var passwordField = document.getElementById('loginPassword');
                if (passwordField) {{
                    passwordField.value = '{password}';
                    ['focus', 'input', 'change'].forEach(eventType => {{
                        passwordField.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
                    }});
                }}
            """)
            
            time.sleep(1)  # Let events propagate
            
            # Submit with JavaScript
            self.driver.execute_script("""
                // Find and submit form
                var forms = document.getElementsByTagName('form');
                for (var i = 0; i < forms.length; i++) {
                    if (forms[i].querySelector('#loginEmail')) {
                        forms[i].submit();
                        return true;
                    }
                }
                return false;
            """)
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login successful
            current_url = self.driver.current_url
            if "login" not in current_url and "account/login" not in current_url:
                return True
            else:
                # Check for error messages
                try:
                    errors = self.driver.find_elements(By.CSS_SELECTOR, ".error, .text-danger, .alert-danger")
                    for err in errors:
                        if err.is_displayed() and err.text:
                            print(f"   Error: {err.text[:100]}")
                except:
                    pass
                
                return False
                
        except Exception as e:
            print(f"   JavaScript login error: {e}")
            return False
    
    def test_access(self):
        """Test if we can access Whydonate"""
        print("\n🌐 Testing Whydonate access...")
        
        test_urls = [
            ("Homepage", "https://whydonate.com"),
            ("Login", "https://whydonate.com/account/login"),
            ("Create Campaign", "https://whydonate.com/en/fundraiser/create")
        ]
        
        for name, url in test_urls:
            try:
                print(f"\n   Testing {name}...")
                self.driver.get(url)
                time.sleep(3)
                
                status = "✅" if self.driver.current_url == url else "⚠️"
                print(f"   {status} {url}")
                print(f"   Title: {self.driver.title[:50]}...")
                
                # Check for blocking
                page_text = self.driver.page_source.lower()
                if "blocked" in page_text or "access denied" in page_text:
                    print(f"   ❌ PAGE BLOCKED (geo restriction)")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def close(self):
        """Close browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("\n✅ Browser closed")

def main():
    """Main test function"""
    print("\n" + "="*70)
    print("VPN-ENABLED WHYDONATE BOT TEST")
    print("="*70)
    
    # Check if user wants VPN check
    vpn_check = input("\nCheck VPN/location first? (y/n): ").lower().strip()
    if vpn_check == 'y':
        import vpn_check
        vpn_check.check_vpn_status()
    
    # Get credentials
    print("\n" + "-"*70)
    print("WHYDONATE CREDENTIALS")
    print("-"*70)
    
    username = input("\nEmail: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Credentials required.")
        return
    
    # Initialize bot
    bot = VPNWhydonateBot(vpn_required=True)
    
    try:
        # Test access first
        bot.test_access()
        
        # Try login
        input("\nPress Enter to attempt login...")
        
        success = bot.login_with_retry(username, password, max_retries=3)
        
        if success:
            print("\n🎉 LOGIN SUCCESSFUL!")
            print(f"   Current URL: {bot.driver.current_url}")
            print(f"   Title: {bot.driver.title}")
            
            # Test campaign creation access
            print("\n🔗 Testing campaign creation access...")
            bot.driver.get("https://whydonate.com/en/fundraiser/create")
            time.sleep(3)
            
            if "create" in bot.driver.current_url:
                print("   ✅ Can access campaign creation!")
            else:
                print(f"   ⚠️  Might need additional permissions")
                print(f"   Current page: {bot.driver.current_url}")
        else:
            print("\n❌ LOGIN FAILED")
            print("   Possible reasons:")
            print("   1. Wrong credentials")
            print("   2. Geo-blocking (need VPN in Netherlands)")
            print("   3. Account needs verification")
            print("   4. CAPTCHA/2FA required")
            
            # Take screenshot for debugging
            try:
                bot.driver.save_screenshot(str(BASE_DIR / "data" / "login_failed.png"))
                print(f"\n   Screenshot saved: data/login_failed.png")
            except:
                pass
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        bot.close()

if __name__ == "__main__":
    (BASE_DIR / "data").mkdir(exist_ok=True)
    main()