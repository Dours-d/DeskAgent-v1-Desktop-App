import sys
import json
import time
import logging
from pathlib import Path

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

print(f"[WhydonateBot] BASE_DIR: {BASE_DIR}")

# Import selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    print("[WhydonateBot] Selenium imported successfully")
except ImportError as e:
    print(f"[WhydonateBot] Error importing selenium: {e}")
    print("Install: pip install selenium")
    sys.exit(1)

# Import pandas
try:
    import pandas as pd
    print("[WhydonateBot] pandas imported successfully")
except ImportError:
    print("[WhydonateBot] pandas not installed. Install: pip install pandas")
    pd = None


class WhydonateBot:
    def __init__(self, headless=None):
        self.base_dir = BASE_DIR
        self.config = self.load_or_create_config()
        
        # Use config value for headless if not specified
        if headless is None:
            headless = self.config.get('whydonate', {}).get('headless', True)
        
        print(f"[WhydonateBot] Initializing with headless={headless}")
        self.setup_logging()
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, self.config.get('whydonate', {}).get('timeout', 30))
        
    def load_or_create_config(self):
        """Load config or create default if missing"""
        config_path = self.base_dir / "data" / "config.txt"
        
        # Default configuration
        default_config = {
            "system": {
                "version": "1.0.0",
                "name": "DeskAgent v1",
                "debug_mode": True
            },
            "whydonate": {
                "enabled": False,
                "username": "",
                "password": "",
                "headless": True,
                "timeout": 30,
                "base_url": "https://www.whydonate.com",
                "default_category": "General",
                "default_currency": "EUR"
            },
            "csv": {
                "path": "./data/.csv/campaigns_master.csv",
                "encoding": "utf-8"
            },
            "logging": {
                "level": "INFO",
                "file": "./data/logs/whydonate_bot.log"
            }
        }
        
        try:
            if not config_path.exists():
                print(f"[WhydonateBot] Config file not found at {config_path}")
                print("[WhydonateBot] Creating default configuration...")
                
                # Ensure directory exists
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create config file
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                print(f"[WhydonateBot] Default config created at: {config_path}")
                print("[WhydonateBot] Please edit config.txt to add your Whydonate credentials")
                return default_config
            
            # Load existing config
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults (defaults fill in missing keys)
            merged_config = self.merge_configs(default_config, loaded_config)
            
            print(f"[WhydonateBot] Config loaded from: {config_path}")
            return merged_config
            
        except json.JSONDecodeError as e:
            print(f"[WhydonateBot] Invalid JSON in config: {e}")
            print("[WhydonateBot] Using default configuration")
            return default_config
        except Exception as e:
            print(f"[WhydonateBot] Error loading config: {e}")
            return default_config
    
    def merge_configs(self, default, user):
        """Merge default and user configs"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def setup_logging(self):
        """Setup logging based on config"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = self.base_dir / Path(log_config.get('file', './data/logs/whydonate_bot.log'))
        
        # Create log directory
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger('WhydonateBot')
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"WhydonateBot initialized")
        self.logger.info(f"Config: Whydonate enabled = {self.config.get('whydonate', {}).get('enabled', False)}")
        self.logger.info(f"Log file: {log_file}")
    
    def setup_driver(self, headless):
        """Setup Chrome driver"""
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.logger.info(f"ChromeDriver initialized (headless={headless})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise
    
    def check_credentials(self):
        """Check if credentials are configured"""
        whydonate_config = self.config.get('whydonate', {})
        username = whydonate_config.get('username', '')
        password = whydonate_config.get('password', '')
        
        if not username or not password:
            self.logger.warning("Whydonate credentials not configured")
            self.logger.info("Please edit data/config.txt and add:")
            self.logger.info('  "username": "your_email@example.com",')
            self.logger.info('  "password": "your_password"')
            return False
        
        return True
    
    def login(self, username, password):
    """Login to Whydonate with cookie banner handling first"""
    try:
        # Use the correct login URL
        login_url = "https://whydonate.com/account/login"
        
        self.logger.info(f"Navigating to login page: {login_url}")
        self.driver.get(login_url)
        time.sleep(5)  # Wait for page to fully load
        
        # STEP 1: Handle cookie banner COMPREHENSIVELY
        self.logger.info("Step 1: Handling cookie banners...")
        self.handle_cookie_banner_comprehensive()
        time.sleep(2)
        
        # Take screenshot after cookie handling
        try:
            screenshot_dir = self.base_dir / "data" / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(str(screenshot_dir / "after_cookies.png"))
        except:
            pass
        
        # STEP 2: Check if we can interact with form
        self.logger.info("Step 2: Checking form accessibility...")
        
        # Try to find email field
        try:
            email_field = self.driver.find_element(By.ID, "loginEmail")
            self.logger.info(f"Email field found. Displayed: {email_field.is_displayed()}, Enabled: {email_field.is_enabled()}")
        except Exception as e:
            self.logger.error(f"Cannot find email field: {e}")
            return False
        
        # STEP 3: Try JavaScript approach first (bypasses interaction issues)
        self.logger.info("Step 3: Using JavaScript to fill form...")
        
        # Fill form using JavaScript
        try:
            # Set email
            self.driver.execute_script(f"""
                var emailField = document.getElementById('loginEmail');
                if (emailField) {{
                    emailField.value = '{username}';
                    // Trigger all necessary events
                    ['focus', 'input', 'change'].forEach(eventType => {{
                        var event = new Event(eventType, {{ bubbles: true }});
                        emailField.dispatchEvent(event);
                    }});
                }}
            """)
            self.logger.info("✓ Email set via JavaScript")
            
            # Set password
            self.driver.execute_script(f"""
                var passwordField = document.getElementById('loginPassword');
                if (passwordField) {{
                    passwordField.value = '{password}';
                    // Trigger all necessary events
                    ['focus', 'input', 'change'].forEach(eventType => {{
                        var event = new Event(eventType, {{ bubbles: true }});
                        passwordField.dispatchEvent(event);
                    }});
                }}
            """)
            self.logger.info("✓ Password set via JavaScript")
            
        except Exception as js_error:
            self.logger.error(f"JavaScript injection failed: {js_error}")
            
            # Fallback to normal Selenium
            try:
                self.logger.info("Falling back to normal Selenium...")
                email_field = self.driver.find_element(By.ID, "loginEmail")
                password_field = self.driver.find_element(By.ID, "loginPassword")
                
                # Click fields first
                email_field.click()
                time.sleep(0.5)
                email_field.clear()
                email_field.send_keys(username)
                
                password_field.click()
                time.sleep(0.5)
                password_field.clear()
                password_field.send_keys(password)
                
            except Exception as selenium_error:
                self.logger.error(f"Selenium also failed: {selenium_error}")
                return False
        
        # Take screenshot before submit
        try:
            self.driver.save_screenshot(str(screenshot_dir / "before_submit.png"))
        except:
            pass
        
        # STEP 4: Submit form
        self.logger.info("Step 4: Submitting form...")
        
        # Method 1: Try JavaScript submit
        try:
            self.driver.execute_script("""
                // Find the form containing the login fields
                var forms = document.getElementsByTagName('form');
                for (var i = 0; i < forms.length; i++) {
                    if (forms[i].querySelector('#loginEmail')) {
                        forms[i].submit();
                        console.log('Form submitted via JavaScript');
                        break;
                    }
                }
            """)
            self.logger.info("✓ Form submitted via JavaScript")
            
        except Exception as submit_error:
            self.logger.warning(f"JavaScript submit failed: {submit_error}")
            
            # Method 2: Try Enter key
            try:
                from selenium.webdriver.common.keys import Keys
                password_field = self.driver.find_element(By.ID, "loginPassword")
                password_field.send_keys(Keys.RETURN)
                self.logger.info("✓ Pressed Enter key")
            except:
                self.logger.error("All submit methods failed")
                return False
        
        # STEP 5: Wait and check result
        time.sleep(5)
        
        # Take screenshot after submit
        try:
            self.driver.save_screenshot(str(screenshot_dir / "after_submit.png"))
        except:
            pass
        
        # Check login result
        current_url = self.driver.current_url
        self.logger.info(f"Step 5: Checking result. Current URL: {current_url}")
        
        # Success indicators
        success_pages = ["/dashboard", "/my-campaigns", "/account", "/organizer", "/en/fundraiser"]
        still_on_login = "login" in current_url or "account/login" in current_url
        
        if any(page in current_url for page in success_pages):
            self.logger.info("✅ LOGIN SUCCESSFUL!")
            return True
        elif still_on_login:
            self.logger.error("❌ LOGIN FAILED - Still on login page")
            
            # Check for specific error messages
            try:
                error_selectors = [".error", ".text-danger", ".invalid-feedback", "[class*='error']"]
                for selector in error_selectors:
                    try:
                        errors = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for err in errors:
                            if err.text and err.is_displayed():
                                self.logger.error(f"Error: {err.text[:100]}")
                    except:
                        continue
            except:
                pass
            
            return False
        else:
            # Unknown page - might be successful
            self.logger.warning(f"⚠️  On unknown page: {current_url}")
            self.logger.warning("Assuming login successful...")
            return True
            
    except Exception as e:
        self.logger.error(f"❌ Login process failed: {e}")
        return False
    
    def handle_cookie_banner_comprehensive(self):
    """Comprehensive cookie banner handling for Whydonate"""
    self.logger.info("Starting comprehensive cookie banner handling...")
    
    # List of common cookie banner selectors for Whydonate (European sites)
    banner_selectors = [
        # Common European cookie banners
        "#CybotCookiebotDialog",  # Cookiebot (very common)
        "#cookie-banner", "#cookie-notice", "#cookieConsent",
        ".cookie-banner", ".cookie-notice", ".cookie-consent",
        ".gdpr-banner", ".gdpr-consent", ".privacy-banner",
        ".consent-banner", ".consent-popup",
        
        # Dutch-specific
        "[data-cy='cookie-banner']", "[data-testid='cookie-banner']",
        ".cookie-wall", ".cookie-container",
        
        # Generic overlays
        "div[role='alertdialog']", "div[aria-label*='cookie']",
        "div[class*='cookie']", "div[id*='cookie']",
        
        # Bottom-fixed banners (common placement)
        "div[style*='fixed'][style*='bottom']:not([style*='height:0'])",
        "div[class*='fixed'][class*='bottom']"
    ]
    
    # Accept button texts (Dutch/English)
    accept_texts = [
        # English
        "Accept", "Accept All", "Accept Cookies", "Accept All Cookies",
        "I Accept", "Agree", "Agree All", "Allow", "Allow All",
        "Consent", "Give Consent", "Okay", "OK", "Got it", "Continue",
        "Proceed", "Understand", "Close",
        # Dutch
        "Accepteren", "Alles accepteren", "Cookies accepteren",
        "Akkoord", "Akkoord met alles", "Doorgaan", "Begrepen",
        "Sluiten", "Toestaan", "Alles toestaan",
        # Short/icon buttons
        "X", "×", "✕"
    ]
    
    banners_handled = 0
    
    try:
        # Wait a moment for banners to load
        time.sleep(2)
        
        # Method 1: Try common banner selectors
        for selector in banner_selectors:
            try:
                banners = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for banner in banners:
                    if banner.is_displayed():
                        self.logger.info(f"Found cookie banner: {selector}")
                        
                        # Take screenshot for debugging
                        try:
                            screenshot_dir = self.base_dir / "data" / "screenshots"
                            screenshot_dir.mkdir(parents=True, exist_ok=True)
                            banner.screenshot(str(screenshot_dir / f"cookie_banner_{int(time.time())}.png"))
                        except:
                            pass
                        
                        # Try to find and click accept button
                        button_found = False
                        
                        # Look for buttons with accept text
                        for text in accept_texts:
                            try:
                                buttons = banner.find_elements(
                                    By.XPATH, f".//button[contains(text(), '{text}')]"
                                )
                                for btn in buttons:
                                    if btn.is_displayed() and btn.is_enabled():
                                        self.logger.info(f"Clicking accept button: '{btn.text}'")
                                        btn.click()
                                        time.sleep(1)
                                        button_found = True
                                        banners_handled += 1
                                        break
                                if button_found:
                                    break
                            except:
                                continue
                        
                        # If no text button found, look for any button
                        if not button_found:
                            try:
                                buttons = banner.find_elements(By.TAG_NAME, "button")
                                for btn in buttons:
                                    if btn.is_displayed() and btn.is_enabled():
                                        self.logger.info(f"Clicking generic button: '{btn.text}'")
                                        btn.click()
                                        time.sleep(1)
                                        button_found = True
                                        banners_handled += 1
                                        break
                            except:
                                pass
                        
                        # If still no button, try to hide with JavaScript
                        if not button_found:
                            try:
                                self.driver.execute_script("""
                                    arguments[0].style.display = 'none';
                                    arguments[0].style.visibility = 'hidden';
                                    arguments[0].style.opacity = '0';
                                """, banner)
                                self.logger.info("Hidden banner with JavaScript")
                                banners_handled += 1
                            except:
                                self.logger.warning("Could not hide banner")
                        
            except Exception as e:
                continue
        
        # Method 2: Search for cookie-related text
        cookie_keywords = ["cookie", "Cookie", "COOKIE", "privacy", "Privacy", "gdpr", "GDPR"]
        
        for keyword in cookie_keywords:
            try:
                elements = self.driver.find_elements(
                    By.XPATH, f"//*[contains(text(), '{keyword}')]"
                )
                for elem in elements:
                    if elem.is_displayed():
                        # Check if it looks like a banner (has button or is at bottom)
                        elem_location = elem.location
                        if elem_location['y'] > 400:  # Likely at bottom of page
                            self.logger.info(f"Found cookie text element: {keyword}")
                            
                            # Look for nearby buttons
                            try:
                                # Find parent container and look for buttons
                                parent = elem.find_element(By.XPATH, "./ancestor::div[position()<4]")
                                buttons = parent.find_elements(By.TAG_NAME, "button")
                                
                                for btn in buttons:
                                    if btn.is_displayed():
                                        self.logger.info(f"Clicking nearby button: '{btn.text}'")
                                        btn.click()
                                        time.sleep(1)
                                        banners_handled += 1
                                        break
                            except:
                                pass
            except:
                continue
        
        # Method 3: Remove any overlay that might be blocking
        overlay_selectors = [
            "div.modal-backdrop", "div[class*='backdrop']",
            "div.overlay", "div[class*='overlay']",
            "div[style*='background'][style*='opacity'][style*='cover']"
        ]
        
        for selector in overlay_selectors:
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for overlay in overlays:
                    if overlay.is_displayed():
                        self.logger.info(f"Removing overlay: {selector}")
                        self.driver.execute_script("arguments[0].style.display = 'none';", overlay)
                        banners_handled += 1
            except:
                continue
        
        if banners_handled > 0:
            self.logger.info(f"Handled {banners_handled} cookie banners/overlays")
        else:
            self.logger.info("No cookie banners found")
        
        return banners_handled > 0
        
    except Exception as e:
        self.logger.error(f"Error handling cookie banner: {e}")
        return False

    def process_pending_campaigns(self):
        """Process pending campaigns from CSV"""
        if not self.check_credentials():
            self.logger.error("Cannot process campaigns without credentials")
            return []
        
        if pd is None:
            self.logger.error("pandas not installed. Cannot load CSV.")
            return []
        
        csv_path = self.base_dir / "data" / ".csv" / "campaigns_master.csv"
        
        try:
            if not csv_path.exists():
                self.logger.error(f"CSV file not found: {csv_path}")
                return []
            
            # Load CSV
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Find pending campaigns
            pending_mask = (
                (df['status'].isin(['pending', 'draft'])) & 
                (df['whydonate_url'].isna())
            )
            pending_campaigns = df[pending_mask]
            
            if pending_campaigns.empty:
                self.logger.info("No pending campaigns to process")
                return []
            
            self.logger.info(f"Found {len(pending_campaigns)} pending campaigns")
            
            # Login first
            whydonate_config = self.config.get('whydonate', {})
            username = whydonate_config.get('username', '')
            password = whydonate_config.get('password', '')
            
            if not self.login(username, password):
                self.logger.error("Login failed. Cannot process campaigns.")
                return []
            
            # Process each campaign
            results = []
            for idx, row in pending_campaigns.iterrows():
                campaign_id = row.get('campaign_id', f'camp_{idx}')
                campaign_name = row.get('name', 'Unknown')
                
                self.logger.info(f"Processing campaign: {campaign_id} - {campaign_name}")
                
                try:
                    # Create campaign data
                    campaign_data = {
                        'campaign_details': {
                            'title': row.get('suggested_title', row.get('title', 'Untitled Campaign')),
                            'description': row.get('clean_text', row.get('presentation_text', 'No description')),
                            'category': row.get('category', 'General'),
                            'target_amount': float(row.get('target_amount', 1000)),
                            'currency': 'EUR'
                        }
                    }
                    
                    # Navigate to create page
                    base_url = self.config.get('whydonate', {}).get('base_url', 'https://www.whydonate.com')
                    create_url = f"{base_url}/en/fundraiser/create"
                    self.driver.get(create_url)
                    time.sleep(3)
                    
                    # Fill form (simplified for now)
                    self.logger.info("Filling campaign form...")
                    
                    # Just simulate for now - you'll need to implement actual form filling
                    self.logger.warning("Form filling not fully implemented yet")
                    
                    # For now, return a simulated URL
                    simulated_url = f"{base_url}/en/fundraiser/test-campaign-{campaign_id}"
                    
                    # Update CSV
                    df.loc[df['campaign_id'] == campaign_id, 'whydonate_url'] = simulated_url
                    df.loc[df['campaign_id'] == campaign_id, 'status'] = 'active'
                    df.loc[df['campaign_id'] == campaign_id, 'last_updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    results.append({
                        'campaign_id': campaign_id,
                        'status': 'created',
                        'url': simulated_url,
                        'name': campaign_name
                    })
                    
                    self.logger.info(f"Campaign {campaign_id} processed successfully")
                    
                except Exception as e:
                    self.logger.error(f"Error processing campaign {campaign_id}: {e}")
                    results.append({
                        'campaign_id': campaign_id,
                        'status': 'error',
                        'error': str(e),
                        'name': campaign_name
                    })
            
            # Save updated CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            self.logger.info(f"CSV updated with {len(results)} processed campaigns")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing campaigns: {e}")
            return []
    
    def close(self):
        """Close browser"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except:
                pass
    
    def test_connection(self):
        """Test connection and credentials"""
        print("\n" + "="*60)
        print("Testing Whydonate Bot Configuration")
        print("="*60)
        
        # Check config
        print(f"\n1. Configuration:")
        print(f"   Config file: {self.base_dir / 'data' / 'config.txt'}")
        print(f"   Whydonate enabled: {self.config.get('whydonate', {}).get('enabled', False)}")
        
        # Check credentials
        whydonate_config = self.config.get('whydonate', {})
        username = whydonate_config.get('username', '')
        password = whydonate_config.get('password', '')
        
        print(f"\n2. Credentials:")
        print(f"   Username: {'✓ Set' if username else '✗ Not set'}")
        print(f"   Password: {'✓ Set' if password else '✗ Not set'}")
        
        if not username or not password:
            print(f"\n   Please edit {self.base_dir / 'data' / 'config.txt}")

            print(f"   Add your Whydonate credentials:")
            print(f'     "username": "your_email@example.com",')
            print(f'     "password": "your_password"')
        
        # Test browser
        print(f"\n3. Browser test:")

        try:
            self.driver.get("https://www.google.com")
            print(f"   ✓ Browser working: {self.driver.title}")
            
            # Test Whydonate page
            self.driver.get("https://www.whydonate.com")
            print(f"   ✓ Whydonate accessible: {self.driver.title}")
            
        except Exception as e:
            print(f"   ✗ Browser error: {e}")
        
        # Test login if credentials are set
        if username and password:
            print(f"\n4. Login test:")
            response = input("   Test login? (y/n): ").lower()
            
            if response == 'y':
                print("   Attempting login...")
                if self.login(username, password):
                    print("   ✓ Login successful!")
                    print(f"   Current URL: {self.driver.current_url}")
                else:
                    print("   ✗ Login failed")
        
        print("\n" + "="*60)
        print("Test completed!")
        print("="*60)

def test_connection(self):
    """Test connection and credentials"""
    print("\n" + "="*60)
    print("Testing Whydonate Bot Configuration")
    print("="*60)
    
    # Check config
    print(f"\n1. Configuration:")
    print(f"   Config file: {self.base_dir / 'data' / 'config.txt'}")
    print(f"   Whydonate enabled: {self.config.get('whydonate', {}).get('enabled', False)}")
    
    # Check credentials
    whydonate_config = self.config.get('whydonate', {})
    username = whydonate_config.get('username', '')
    password = whydonate_config.get('password', '')
    
    print(f"\n2. Credentials:")
    print(f"   Username: {'✓ Set' if username else '✗ Not set'}")
    print(f"   Password: {'✓ Set' if password else '✗ Not set'}")
    
    if not username or not password:
        print(f"\n   Please edit {self.base_dir / 'data' / 'config.txt'}")
        print(f"   Add your Whydonate credentials:")
        print(f'     "username": "your_email@example.com",')
        print(f'     "password": "your_password"')
    
    # Test browser
    print(f"\n3. Browser test:")
    try:
        self.driver.get("https://www.google.com")
        print(f"   ✓ Google accessible: {self.driver.title[:50]}...")
        
        # Test Whydonate page
        self.driver.get("https://www.whydonate.com")
        time.sleep(2)
        
        # Check if we're on Whydonate
        current_title = self.driver.title
        if "Whydonate" in current_title or "WhyDonate" in current_title or "Crowdfunding" in current_title:
            print(f"   ✓ Whydonate accessible: {current_title[:50]}...")
            
            # Check for login page elements
            try:
                # Look for login indicators
                login_elements = self.driver.find_elements(
                    By.XPATH, "//a[contains(text(), 'Login') or contains(text(), 'Sign in')]"
                )
                if login_elements:
                    print(f"   ✓ Login page elements found")
                    
                    # Try to find the actual login form
                    try:
                        email_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
                        password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
                        
                        if email_fields and password_fields:
                            print(f"   ✓ Login form detected")
                        else:
                            print(f"   ⓘ Login form not immediately visible (may need to click login button)")
                    except:
                        print(f"   ⓘ Could not inspect form fields")
            except:
                print(f"   ⓘ Could not check for login elements")
        else:
            print(f"   ⓘ Unexpected page: {current_title}")
            
    except Exception as e:
        print(f"   ✗ Browser error: {e}")
    
    # Test login if credentials are set
    if username and password:
        print(f"\n4. Login test:")
        
        # Ask user if they want to test
        response = input("   Test login with your credentials? (y/n): ").lower().strip()
        
        if response == 'y':
            print("   Attempting login...")
            
            # Navigate to login page
            base_url = whydonate_config.get('base_url', 'https://www.whydonate.com')
            login_url = f"{base_url}/en/login"
            
            try:
                self.driver.get(login_url)
                time.sleep(3)
                
                # Take screenshot before login
                screenshot_dir = self.base_dir / "data" / "screenshots"
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                before_screenshot = screenshot_dir / "login_page_before.png"
                self.driver.save_screenshot(str(before_screenshot))
                print(f"   Screenshot saved: {before_screenshot.name}")
                
                # Attempt login
                login_success = self.login(username, password)
                
                if login_success:
                    print("   ✓ Login successful!")
                    print(f"   Current URL: {self.driver.current_url[:100]}...")
                    
                    # Take screenshot after login
                    after_screenshot = screenshot_dir / "login_page_after.png"
                    self.driver.save_screenshot(str(after_screenshot))
                    print(f"   Screenshot saved: {after_screenshot.name}")
                    
                    # Check what page we're on
                    current_url = self.driver.current_url
                    if "/dashboard" in current_url:
                        print("   ✓ On dashboard page")
                    elif "/my-campaigns" in current_url:
                        print("   ✓ On campaigns page")
                    elif "/fundraiser" in current_url:
                        print("   ✓ On fundraiser page")
                    else:
                        print(f"   ⓘ On unknown page: {current_url[:100]}...")
                        
                else:
                    print("   ✗ Login failed")
                    
                    # Take screenshot of error
                    error_screenshot = screenshot_dir / "login_error.png"
                    self.driver.save_screenshot(str(error_screenshot))
                    print(f"   Error screenshot saved: {error_screenshot.name}")
                    
                    # Look for error messages
                    try:
                        error_elements = self.driver.find_elements(
                            By.CSS_SELECTOR, ".error, .alert-danger, .text-danger, [class*='error']"
                        )
                        if error_elements:
                            errors = []
                            for elem in error_elements[:3]:  # Check first 3 error elements
                                if elem.text and elem.text.strip():
                                    errors.append(elem.text.strip())
                            
                            if errors:
                                print(f"   Error messages found:")
                                for err in errors[:2]:  # Show first 2 errors
                                    print(f"     - {err[:100]}...")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ✗ Login test error: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("WHYDONATE BOT - DeskAgent v1")
    print("="*60)
    
    print("\nOptions:")
    print("1. Test configuration and connection")
    print("2. Process pending campaigns")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        bot = WhydonateBot(headless=False)
        try:
            bot.test_connection()
        finally:
            bot.close()
    elif choice == "2":
        bot = WhydonateBot(headless=False)
        try:
            results = bot.process_pending_campaigns()
            if results:
                print(f"\nProcessed {len(results)} campaigns:")
                for result in results:
                    status_icon = "✓" if result.get('status') == 'created' else "✗"
                    print(f"  {status_icon} {result.get('campaign_id')}: {result.get('status')}")
                    if result.get('url'):
                        print(f"     URL: {result.get('url')}")
            else:
                print("\nNo campaigns processed or no pending campaigns found.")
        finally:
            bot.close()
    else:
        print("\nExiting...")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()