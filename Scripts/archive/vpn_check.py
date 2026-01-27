import sys
from pathlib import Path
import requests
import json

BASE_DIR = Path(__file__).parent.parent

def check_vpn_status():
    """Check if VPN is active and location"""
    print("\n" + "="*60)
    print("VPN & GEO-LOCATION CHECK")
    print("="*60)
    
    try:
        # Test IP and location
        response = requests.get('https://ipapi.co/json/', timeout=10)
        data = response.json()
        
        print(f"\n🌍 YOUR CURRENT LOCATION:")
        print(f"  IP Address: {data.get('ip', 'Unknown')}")
        print(f"  Country: {data.get('country_name', 'Unknown')}")
        print(f"  Region: {data.get('region', 'Unknown')}")
        print(f"  City: {data.get('city', 'Unknown')}")
        print(f"  ISP: {data.get('org', 'Unknown')}")
        
        # Check if in Netherlands (Whydonate's home country)
        is_nl = data.get('country_code') == 'NL'
        print(f"\n🇳🇱 In Netherlands: {'✅ YES' if is_nl else '❌ NO'}")
        
        if not is_nl:
            print("\n⚠️  WARNING: You might need VPN set to Netherlands!")
            print("   Whydonate may restrict access from other countries.")
        
        # Save location info
        with open(BASE_DIR / "data" / "location.json", "w") as f:
            json.dump(data, f, indent=2)
        
        return data
        
    except Exception as e:
        print(f"\n❌ Could not check location: {e}")
        print("   Make sure you're connected to the internet/VPN")
        return None

def test_whydonate_access():
    """Test if Whydonate is accessible from current location"""
    print("\n" + "="*60)
    print("WHYDONATE ACCESS TEST")
    print("="*60)
    
    test_urls = [
        "https://whydonate.com",
        "https://whydonate.com/account/login",
        "https://whydonate.com/en/fundraiser/create"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {url}: HTTP {response.status_code}")
            
        except requests.exceptions.Timeout:
            print(f"❌ {url}: TIMEOUT (might be blocked)")
        except Exception as e:
            print(f"❌ {url}: ERROR - {e}")

if __name__ == "__main__":
    (BASE_DIR / "data").mkdir(exist_ok=True)
    
    location = check_vpn_status()
    if location:
        test_whydonate_access()
    
    input("\nPress Enter to exit...")