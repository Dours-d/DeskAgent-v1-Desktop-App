import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print(f"Python path: {sys.path}")

try:
    # Import the bot
    from scripts.whydonate_bot import WhydonateBot
    print("Successfully imported WhydonateBot")
except ImportError as e:
    print(f"Import error: {e}")
    print("\nTrying alternative import method...")
    
    # Try direct import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "whydonate_bot", 
        current_dir / "whydonate_bot.py"
    )
    whydonate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(whydonate_module)
    WhydonateBot = whydonate_module.WhydonateBot
    print("Successfully loaded WhydonateBot directly")

def test_bot():
    """Test the Whydonate bot"""
    print("\n" + "="*60)
    print("Testing Whydonate Bot...")
    print("="*60)
    
    try:
        # Initialize bot (non-headless for debugging)
        print("Initializing bot...")
        bot = WhydonateBot(headless=False)
        
        # Test loading config
        print("\n1. Testing config loading...")
        config = bot.load_config()
        if not config:
            print("ERROR: Config file not found or invalid")
            print(f"Expected at: {bot.get_config_path()}")
            
            # Check if file exists
            config_path = bot.get_config_path()
            if not config_path.exists():
                print(f"File does not exist: {config_path}")
                print("Creating default config...")
                
                # Create default config
                default_config = {
                    "system": {
                        "version": "1.0.0",
                        "data_path": str(bot.base_dir / "data")
                    },
                    "whydonate": {
                        "enabled": False,
                        "username": "",
                        "password": "",
                        "auto_login": False
                    }
                }
                
                config_path.parent.mkdir(parents=True, exist_ok=True)
                import json
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default config at: {config_path}")
            return
        
        print(f"✓ Config loaded successfully")
        print(f"  Username: {config.get('whydonate', {}).get('username', 'Not set')}")
        print(f"  Enabled: {config.get('whydonate', {}).get('enabled', False)}")
        
        # Test loading campaigns
        print("\n2. Testing CSV loading...")
        try:
            import pandas as pd
            df = bot.load_campaigns_from_csv()
            print(f"✓ Loaded {len(df)} campaigns from CSV")
            
            if len(df) > 0:
                print("\nSample campaigns:")
                for i in range(min(3, len(df))):
                    row = df.iloc[i]
                    print(f"  {i+1}. {row.get('campaign_id', 'N/A')}: {row.get('name', 'N/A')} - {row.get('title', 'N/A')} [{row.get('status', 'N/A')}]")
            else:
                print("  No campaigns found in CSV")
                
        except ImportError:
            print("✗ pandas not installed. Install with: pip install pandas")
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
        
        # Test browser functionality
        print("\n3. Testing browser...")
        print(f"  Browser: {bot.driver.name}")
        print(f"  Browser version: {bot.driver.capabilities['browserVersion']}")
        
        # Test navigation (without login)
        print("\n4. Testing navigation...")
        try:
            bot.driver.get("https://www.google.com")
            title = bot.driver.title
            print(f"  ✓ Successfully navigated to: {title}")
        except Exception as e:
            print(f"  ✗ Navigation test failed: {e}")
        
        print("\n" + "="*60)
        print("Basic tests completed successfully!")
        print("="*60)
        
        # Ask if user wants to test login
        print("\nDo you want to test Whydonate login? (requires credentials in config)")
        response = input("Enter 'y' to test login, or any other key to skip: ")
        
        if response.lower() == 'y':
            username = config.get('whydonate', {}).get('username', '')
            password = config.get('whydonate', {}).get('password', '')
            
            if not username or not password:
                print("✗ Username or password not set in config")
            else:
                print(f"\nAttempting login with username: {username}")
                print("This will open a browser window...")
                
                if bot.login(username, password):
                    print("✓ Login successful!")
                    print(f"Current URL: {bot.driver.current_url}")
                    
                    # Test campaign creation if user wants
                    print("\nDo you want to test campaign creation?")
                    response2 = input("Enter 'y' to test, or any other key to skip: ")
                    
                    if response2.lower() == 'y':
                        test_campaign_data = {
                            'campaign_details': {
                                'title': 'Test Campaign - Please Ignore',
                                'description': 'This is a test campaign created by DeskAgent bot for testing purposes. Please ignore.',
                                'category': 'General',
                                'target_amount': 100,
                                'currency': 'EUR'
                            }
                        }
                        
                        print("\nCreating test campaign...")
                        result = bot.create_campaign(test_campaign_data)
                        
                        if result:
                            print(f"✓ Campaign created: {result}")
                        else:
                            print("✗ Campaign creation failed")
                    
                else:
                    print("✗ Login failed")
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'bot' in locals():
            print("\nClosing bot...")
            bot.close()
            print("Bot closed.")

if __name__ == "__main__":
    test_bot()
    input("\nPress Enter to exit...")