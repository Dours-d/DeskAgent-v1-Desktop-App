import json
import sys
from pathlib import Path

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

CONFIG_PATH = BASE_DIR / "data" / "config.txt"

def create_default_config():
    """Create default configuration"""
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
            "headless": False,
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
            "file": "./data/logs/deskagent.log"
        }
    }
    
    return default_config

def setup_configuration():
    """Interactive configuration setup"""
    print("\n" + "="*60)
    print("DeskAgent v1 - Configuration Setup")
    print("="*60)
    
    # Load existing config or create default
    if CONFIG_PATH.exists():
        print(f"\nFound existing configuration at: {CONFIG_PATH}")
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("Loaded existing configuration.")
        except:
            print("Error loading config. Creating new configuration.")
            config = create_default_config()
    else:
        print(f"\nCreating new configuration at: {CONFIG_PATH}")
        config = create_default_config()
    
    print("\n" + "-"*60)
    print("WHYDONATE SETTINGS")
    print("-"*60)
    
    # Whydonate credentials
    print("\nWhydonate Credentials (required for automation):")
    print("Leave blank to skip if you don't have credentials yet.")
    
    username = input("Email/Username: ").strip()
    if username:
        config['whydonate']['username'] = username
        config['whydonate']['enabled'] = True
    
    password = input("Password: ").strip()
    if password:
        config['whydonate']['password'] = password
    
    # Browser settings
    print("\nBrowser Settings:")
    headless = input("Run browser in background (headless)? (y/n, default=n): ").strip().lower()
    config['whydonate']['headless'] = headless == 'y'
    
    # Campaign defaults
    print("\nCampaign Defaults:")
    default_category = input("Default category (default=General): ").strip()
    if default_category:
        config['whydonate']['default_category'] = default_category
    
    default_amount = input("Default target amount in EUR (default=1000): ").strip()
    if default_amount and default_amount.isdigit():
        config['whydonate']['default_target'] = int(default_amount)
    
    # Save configuration
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Configuration saved to: {CONFIG_PATH}")
    
    # Show summary
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    print(f"Whydonate Enabled: {config['whydonate']['enabled']}")
    print(f"Username: {config['whydonate']['username'][:3]}..." if config['whydonate']['username'] else "Username: Not set")
    print(f"Password: {'Set' if config['whydonate']['password'] else 'Not set'}")
    print(f"Headless Mode: {config['whydonate']['headless']}")
    print(f"Default Category: {config['whydonate']['default_category']}")
    print("\nYou can edit the configuration manually at any time.")
    print("="*60)
    
    # Test connection if credentials are set
    if config['whydonate']['username'] and config['whydonate']['password']:
        test = input("\nTest Whydonate connection now? (y/n): ").strip().lower()
        if test == 'y':
            test_whydonate_connection(config)

def test_whydonate_connection(config):
    """Test Whydonate connection"""
    print("\nTesting Whydonate connection...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        import time
        
        # Setup browser
        options = webdriver.ChromeOptions()
        if config['whydonate']['headless']:
            options.add_argument('--headless=new')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # Test website access
            print("  Testing website access...")
            driver.get("https://www.whydonate.com")
            time.sleep(2)
            
            if "Whydonate" in driver.title:
                print("  ✓ Website accessible")
                
                # Try login
                print("  Testing login...")
                driver.get("https://www.whydonate.com/en/login")
                time.sleep(2)
                
                # Find and fill form
                try:
                    email_field = driver.find_element(By.NAME, "email")
                    password_field = driver.find_element(By.NAME, "password")
                    
                    email_field.send_keys(config['whydonate']['username'])
                    password_field.send_keys(config['whydonate']['password'])
                    
                    # Find login button
                    login_button = driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Login')]"
                    )
                    login_button.click()
                    time.sleep(3)
                    
                    # Check login success
                    current_url = driver.current_url
                    if "/dashboard" in current_url:
                        print("  ✓ Login successful!")
                    else:
                        print("  ✗ Login may have failed")
                        print(f"    Current URL: {current_url}")
                        
                except Exception as e:
                    print(f"  ✗ Login test error: {e}")
                
            else:
                print(f"  ✗ Unexpected page title: {driver.title}")
                
        finally:
            driver.quit()
            
    except ImportError:
        print("  ✗ Selenium not installed. Install with: pip install selenium")
    except Exception as e:
        print(f"  ✗ Connection test failed: {e}")

if __name__ == "__main__":
    setup_configuration()
    input("\nPress Enter to exit...")