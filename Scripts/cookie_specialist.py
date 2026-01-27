import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_DIR = Path(__file__).parent.parent

def detect_and_handle_cookie_banner(driver):
    """Specialized function to detect and handle cookie banners"""
    print("\n" + "="*60)
    print("COOKIE BANNER DETECTION")
    print("="*60)
    
    # Common cookie banner keywords (Dutch/English)
    cookie_keywords = [
        "cookie", "Cookie", "COOKIE",
        "privacy", "Privacy", "PRIVACY",
        "consent", "Consent", "CONSENT",
        "gdpr", "GDPR",
        "accept", "Accept", "ACCEPT",
        "akkoord", "Akkoord", "AKKOORD",  # Dutch for agree
        "toestemming", "Toestemming"  # Dutch for consent
    ]
    
    # Common accept button texts
    accept_texts = [
        # English
        "Accept", "Accept All", "Accept Cookies", "Accept All Cookies",
        "I Accept", "Agree", "Agree All", "Allow", "Allow All",
        "Consent", "Give Consent", "Okay", "OK", "Got it", "Continue",
        "Proceed", "Understand", "Close", "X",
        # Dutch
        "Accepteren", "Alles accepteren", "Cookies accepteren",
        "Akkoord", "Akkoord met alles", "Doorgaan", "Begrepen",
        "Sluiten", "Toestaan", "Alles toestaan"
    ]
    
    # Take screenshot before
    driver.save_screenshot(str(BASE_DIR / "data" / "before_cookie_check.png"))
    
    print("Looking for cookie banners...")
    
    # Method 1: Look for common cookie banner elements
    banner_selectors = [
        # By common IDs
        "#cookie-banner", "#cookie-notice", "#cookieConsent", "#cookies-notice",
        "#gdpr-consent", "#privacy-consent", "#CybotCookiebotDialog",
        "#cookie-wall", "#cookie-popup",
        
        # By common classes
        ".cookie-banner", ".cookie-notice", ".cookie-consent",
        ".cookie-popup", ".cookie-wall", ".cookie-container",
        ".gdpr-banner", ".gdpr-consent", ".privacy-banner",
        ".consent-banner", ".consent-popup",
        
        # By common attributes
        "[data-testid='cookie-banner']", "[data-cy='cookie-banner']",
        "[role='alertdialog']", "[aria-label*='cookie']",
        "[class*='cookie']", "[id*='cookie']",
        
        # By position (often fixed at bottom)
        "div[style*='fixed'][style*='bottom']",
        "div[class*='fixed'][class*='bottom']"
    ]
    
    banners_found = []
    
    for selector in banner_selectors:
        try:
            banners = driver.find_elements(By.CSS_SELECTOR, selector)
            for banner in banners:
                if banner.is_displayed():
                    banners_found.append({
                        'element': banner,
                        'selector': selector,
                        'text': banner.text[:200] if banner.text else "No text",
                        'location': banner.location,
                        'size': banner.size
                    })
        except:
            continue
    
    print(f"Found {len(banners_found)} potential cookie banners")
    
    # Method 2: Look for elements with cookie-related text
    print("\nSearching for elements with cookie-related text...")
    for keyword in cookie_keywords:
        try:
            elements = driver.find_elements(
                By.XPATH, f"//*[contains(text(), '{keyword}')]"
            )
            for elem in elements:
                if elem.is_displayed():
                    # Check if this is a new banner
                    already_found = False
                    for banner in banners_found:
                        if banner['element'] == elem:
                            already_found = True
                            break
                    
                    if not already_found:
                        banners_found.append({
                            'element': elem,
                            'selector': f"text contains '{keyword}'",
                            'text': elem.text[:200] if elem.text else "No text",
                            'location': elem.location,
                            'size': elem.size
                        })
        except:
            continue
    
    # Remove duplicates
    unique_banners = []
    seen_elements = set()
    for banner in banners_found:
        elem_id = id(banner['element'])
        if elem_id not in seen_elements:
            seen_elements.add(elem_id)
            unique_banners.append(banner)
    
    print(f"\nUnique cookie banners found: {len(unique_banners)}")
    
    # Display banner info
    for i, banner in enumerate(unique_banners):
        print(f"\nBanner {i+1}:")
        print(f"  Selector: {banner['selector']}")
        print(f"  Location: {banner['location']}")
        print(f"  Size: {banner['size']}")
        print(f"  Text preview: {banner['text']}...")
        
        # Take screenshot of individual banner
        try:
            banner['element'].screenshot(str(BASE_DIR / "data" / f"cookie_banner_{i+1}.png"))
            print(f"  Screenshot saved: cookie_banner_{i+1}.png")
        except:
            pass
    
    # Try to close each banner
    print("\n" + "="*60)
    print("ATTEMPTING TO CLOSE COOKIE BANNERS")
    print("="*60)
    
    closed_count = 0
    
    for i, banner in enumerate(unique_banners):
        print(f"\nTrying to close banner {i+1}...")
        
        success = False
        
        # Method A: Look for close/accept buttons inside banner
        for text in accept_texts:
            try:
                # Look for buttons with accept text
                buttons = banner['element'].find_elements(
                    By.XPATH, f".//button[contains(text(), '{text}')]"
                )
                
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        print(f"  Found button: '{btn.text}'")
                        btn.click()
                        print(f"  Clicked button")
                        time.sleep(1)
                        success = True
                        closed_count += 1
                        break
                
                if success:
                    break
            except:
                continue
        
        # Method B: Look for any button in banner
        if not success:
            try:
                buttons = banner['element'].find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        print(f"  Found generic button: '{btn.text}'")
                        btn.click()
                        print(f"  Clicked generic button")
                        time.sleep(1)
                        success = True
                        closed_count += 1
                        break
            except:
                pass
        
        # Method C: Look for close buttons (X)
        if not success:
            try:
                close_buttons = banner['element'].find_elements(
                    By.CSS_SELECTOR, "button.close, .close-button, [aria-label='Close'], [aria-label='Sluiten']"
                )
                for btn in close_buttons:
                    if btn.is_displayed():
                        print(f"  Found close button (X)")
                        btn.click()
                        print(f"  Clicked close button")
                        time.sleep(1)
                        success = True
                        closed_count += 1
                        break
            except:
                pass
        
        # Method D: Try to hide with JavaScript
        if not success:
            try:
                driver.execute_script("""
                    arguments[0].style.display = 'none';
                    arguments[0].style.visibility = 'hidden';
                """, banner['element'])
                print(f"  Hidden banner with JavaScript")
                success = True
                closed_count += 1
            except:
                print(f"  Could not hide banner")
        
        if success:
            print(f"  ✓ Banner {i+1} handled")
        else:
            print(f"  ✗ Could not handle banner {i+1}")
    
    # Take screenshot after handling
    driver.save_screenshot(str(BASE_DIR / "data" / "after_cookie_handling.png"))
    
    print(f"\nTotal banners handled: {closed_count}/{len(unique_banners)}")
    print("="*60)
    
    return closed_count > 0

def test_cookie_blocking():
    """Test if cookie banner is blocking interaction"""
    print("\n" + "="*60)
    print("TESTING COOKIE BANNER BLOCKING")
    print("="*60)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Go to Whydonate login page
        print("\n1. Loading Whydonate login page...")
        driver.get("https://whydonate.com/account/login")
        time.sleep(5)  # Wait for page to fully load
        
        print(f"   URL: {driver.current_url}")
        print(f"   Title: {driver.title}")
        
        # Detect and handle cookie banners
        cookie_handled = detect_and_handle_cookie_banner(driver)
        
        # Test if we can interact with login form
        print("\n" + "="*60)
        print("TESTING FORM INTERACTION AFTER COOKIE HANDLING")
        print("="*60)
        
        # Try to find and interact with email field
        print("\nTrying to interact with email field...")
        try:
            email_field = driver.find_element(By.ID, "loginEmail")
            
            print(f"  Email field found")
            print(f"  Displayed: {email_field.is_displayed()}")
            print(f"  Enabled: {email_field.is_enabled()}")
            
            # Try to click it
            try:
                email_field.click()
                print("  ✓ Email field is clickable")
                
                # Try to type
                email_field.send_keys("test@example.com")
                print("  ✓ Can type in email field")
                
            except Exception as click_error:
                print(f"  ✗ Cannot click email field: {click_error}")
                
                # Try JavaScript as fallback
                try:
                    driver.execute_script("""
                        arguments[0].click();
                        arguments[0].value = 'test@example.com';
                    """, email_field)
                    print("  ✓ Used JavaScript to interact with email field")
                except Exception as js_error:
                    print(f"  ✗ JavaScript also failed: {js_error}")
                    
        except Exception as e:
            print(f"  ✗ Cannot find email field: {e}")
        
        # Try to find and interact with password field
        print("\nTrying to interact with password field...")
        try:
            password_field = driver.find_element(By.ID, "loginPassword")
            
            print(f"  Password field found")
            print(f"  Displayed: {password_field.is_displayed()}")
            print(f"  Enabled: {password_field.is_enabled()}")
            
            # Try to click it
            try:
                password_field.click()
                print("  ✓ Password field is clickable")
                
                # Try to type
                password_field.send_keys("test123")
                print("  ✓ Can type in password field")
                
            except Exception as click_error:
                print(f"  ✗ Cannot click password field: {click_error}")
                
                # Try JavaScript as fallback
                try:
                    driver.execute_script("""
                        arguments[0].click();
                        arguments[0].value = 'test123';
                    """, password_field)
                    print("  ✓ Used JavaScript to interact with password field")
                except Exception as js_error:
                    print(f"  ✗ JavaScript also failed: {js_error}")
                    
        except Exception as e:
            print(f"  ✗ Cannot find password field: {e}")
        
        # Check for overlays that might be blocking
        print("\n" + "="*60)
        print("CHECKING FOR OVERLAYS")
        print("="*60)
        
        overlay_selectors = [
            "div.overlay", "div.modal-backdrop", "div[class*='overlay']",
            "div[style*='background'][style*='opacity']",
            "div[class*='backdrop']", "div[class*='modal']"
        ]
        
        for selector in overlay_selectors:
            try:
                overlays = driver.find_elements(By.CSS_SELECTOR, selector)
                for overlay in overlays:
                    if overlay.is_displayed():
                        print(f"  Found overlay: {selector}")
                        print(f"  Location: {overlay.location}, Size: {overlay.size}")
                        
                        # Try to remove overlay
                        try:
                            driver.execute_script("arguments[0].style.display = 'none';", overlay)
                            print(f"  ✓ Removed overlay with JavaScript")
                        except:
                            print(f"  ✗ Could not remove overlay")
            except:
                pass
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        if cookie_handled:
            print("✅ Cookie banners were detected and handled")
        else:
            print("⚠️  No cookie banners detected or could not handle them")
        
        print("\nCheck the screenshots in the 'data' folder:")
        print("- before_cookie_check.png: Initial page")
        print("- cookie_banner_*.png: Individual banners")
        print("- after_cookie_handling.png: After handling")
        
        print("\nBrowser remains open. You can:")
        print("1. Inspect the page (F12)")
        print("2. Check if any banners are still visible")
        print("3. Try to interact with the form manually")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    (BASE_DIR / "data").mkdir(exist_ok=True)
    test_cookie_blocking()