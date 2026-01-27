import sys
from pathlib import Path

# Add parent to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

print("Testing Whydonate Bot Import...")

try:
    # Try to import the module
    import importlib
    import importlib.util
    
    bot_path = Path(__file__).parent / "whydonate_bot.py"
    print(f"Looking for bot at: {bot_path}")
    
    if bot_path.exists():
        print("File exists!")
        
        # Load module directly
        spec = importlib.util.spec_from_file_location("whydonate_bot_module", bot_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("Module loaded successfully!")
        
        # Test creating bot instance
        print("\nCreating bot instance...")
        bot = module.WhydonateBot(headless=False)
        
        print(f"Bot created successfully!")
        print(f"Base dir: {bot.base_dir}")
        print(f"Config path: {bot.get_config_path()}")
        print(f"CSV path: {bot.get_csv_path()}")
        
        bot.close()
        print("\nTest completed successfully!")
    else:
        print("ERROR: whydonate_bot.py not found!")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to quit...")