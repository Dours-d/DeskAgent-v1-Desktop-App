import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_DIR = Path(__file__).parent.parent

def compare_tests():
    """Compare why one test works and another doesn't"""
    print("\n" + "="*70)
    print("DEBUG: COMPARING TESTS")
    print("="*70)
    
    # Use SAME settings as cookie_specialist.py
    print("\n1. Using SAME settings as cookie_specialist.py...")
    options1 = webdriver.ChromeOptions()
    options1.add_argument('--disable-blink-features=AutomationControlled')
    
    driver1 = webdriver.Chrome(options=options1)
    
    try:
        driver1.get("https://whydonate.com/account/login")
        time.sleep(5)
        
        print(f"   URL: {driver1.current_url}")
        print(f"   Title: {driver1.title}")
        
        # Check element state
        email1 = driver1.find_element(By.ID, "loginEmail")
        print(f"\n   Element state with cookie_specialist settings:")
        print(f"   Displayed: {email1.is_displayed()}")
        print(f"   Enabled: {email1.is_enabled()}")
        
        # Try to interact
        try:
            email1.click()
            print("   ✅ CLICKABLE")
        except:
            print("   ❌ NOT CLICKABLE")
        
        driver1.save_screenshot(str(BASE_DIR / "data" / "test1_state.png"))
        
    finally:
        driver1.quit()
    
    # Use SAME settings as test_whydonate_final.py
    print("\n2. Using SAME settings as test_whydonate_final.py...")
    options2 = webdriver.ChromeOptions()
    options2.add_argument('--disable-blink-features=AutomationControlled')
    options2.add_experimental_option("excludeSwitches", ["enable-automation"])
    options2.add_experimental_option('useAutomationExtension', False)
    
    driver2 = webdriver.Chrome(options=options2)
    
    try:
        driver2.get("https://whydonate.com/account/login")
        time.sleep(5)
        
        print(f"   URL: {driver2.current_url}")
        print(f"   Title: {driver2.title}")
        
        # Check element state
        email2 = driver2.find_element(By.ID, "loginEmail")
        print(f"\n   Element state with final_test settings:")
        print(f"   Displayed: {email2.is_displayed()}")
        print(f"   Enabled: {email2.is_enabled()}")
        
        # Try to interact
        try:
            email2.click()
            print("   ✅ CLICKABLE")
        except:
            print("   ❌ NOT CLICKABLE")
        
        driver2.save_screenshot(str(BASE_DIR / "data" / "test2_state.png"))
        
    finally:
        driver2.quit()
    
    print("\n" + "="*70)
    print("COMPARISON COMPLETE")
    print("="*70)

if __name__ == "__main__":
    (BASE_DIR / "data").mkdir(exist_ok=True)
    compare_tests()