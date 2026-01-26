import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.whydonate_bot import WhydonateBot

def test_bot():
    """Test the Whydonate bot"""
    print("Testing Whydonate Bot...")
    
    # Initialize bot (non-headless for debugging)
    bot = WhydonateBot(headless=False)
    
    try:
        # Test loading config
        config = bot.load_config()
        if not config:
            print("ERROR: Config file not found or invalid")
            print(f"Expected at: {bot.get_config_path()}")
            return
        
        print(f"Config loaded: {config.get('whydonate', {}).get('username', 'No username')}")
        
        # Test loading campaigns
        import pandas as pd
        df = bot.load_campaigns_from_csv()
        print(f"Loaded {len(df)} campaigns from CSV")
        
        if len(df) > 0:
            print("Sample campaign:")
            print(df.iloc[0][['campaign_id', 'name', 'title', 'status']])
        
        # You can add login test here if you have credentials
        # username = config.get('whydonate', {}).get('username', '')
        # password = config.get('whydonate', {}).get('password', '')
        # if username and password:
        #     print("Testing login...")
        #     if bot.login(username, password):
        #         print("Login successful!")
        #     else:
        #         print("Login failed!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        bot.close()
        print("Bot closed.")

if __name__ == "__main__":
    test_bot()
