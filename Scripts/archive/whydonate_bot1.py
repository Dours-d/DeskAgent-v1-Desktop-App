from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import logging
from pathlib import Path

class WhydonateBot:
    def __init__(self, headless=True):
        self.setup_logging()
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('whydonate_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self, headless):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        # For ChromeDriver - make sure you have ChromeDriver installed
        self.driver = webdriver.Chrome(options=options)
        
    def login(self, username, password):
        """Login to Whydonate"""
        try:
            self.logger.info("Navigating to Whydonate login page")
            self.driver.get("https://www.whydonate.com/en/login")
            
            # Wait for login form
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Enter credentials
            email_field.send_keys(username)
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]"
            )
            login_button.click()
            
            # Wait for login to complete
            self.wait.until(
                EC.url_contains("/dashboard")
            )
            
            self.logger.info("Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def create_campaign(self, campaign_data):
        """Create a new fundraising campaign"""
        try:
            self.logger.info("Starting campaign creation")
            
            # Navigate to create campaign page
            self.driver.get("https://www.whydonate.com/en/fundraiser/create")
            time.sleep(2)
            
            # Fill basic information
            self.fill_basic_info(campaign_data)
            
            # Fill story section
            self.fill_story_section(campaign_data)
            
            # Set goal and dates
            self.fill_goal_section(campaign_data)
            
            # Upload image (if provided)
            if campaign_data.get('campaign_image'):
                self.upload_image(campaign_data['campaign_image'])
            
            # Submit campaign
            return self.submit_campaign()
            
        except Exception as e:
            self.logger.error(f"Campaign creation failed: {e}")
            return None
    
    def fill_basic_info(self, data):
        """Fill basic campaign information"""
        try:
            # Title
            title_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "title"))
            )
            title_field.clear()
            title_field.send_keys(data['campaign_details']['title'])
            
            # Category
            category_dropdown = self.driver.find_element(
                By.XPATH, "//select[@name='category']"
            )
            category_dropdown.send_keys(data['campaign_details']['category'])
            
            # Short description
            short_desc = self.driver.find_element(
                By.NAME, "short_description"
            )
            short_desc.send_keys(data['campaign_details']['description'][:150])
            
            self.logger.info("Basic information filled")
            
        except Exception as e:
            self.logger.error(f"Failed to fill basic info: {e}")
            raise
    
    def fill_story_section(self, data):
        """Fill campaign story section"""
        try:
            # Switch to description iframe (if any)
            try:
                iframe = self.driver.find_element(
                    By.XPATH, "//iframe[contains(@title, 'Rich Text Editor')]"
                )
                self.driver.switch_to.frame(iframe)
                
                # Find editor body
                editor = self.driver.find_element(By.TAG_NAME, "body")
                editor.clear()
                editor.send_keys(data['campaign_details']['description'])
                
                self.driver.switch_to.default_content()
            except:
                # Try direct textarea
                description_field = self.driver.find_element(
                    By.NAME, "description"
                )
                description_field.clear()
                description_field.send_keys(data['campaign_details']['description'])
            
            self.logger.info("Story section filled")
            
        except Exception as e:
            self.logger.error(f"Failed to fill story section: {e}")
            raise
    
    def fill_goal_section(self, data):
        """Set fundraising goal"""
        try:
            # Target amount
            goal_field = self.driver.find_element(
                By.NAME, "goal_amount"
            )
            goal_field.clear()
            goal_field.send_keys(str(data['campaign_details']['target_amount']))
            
            # Currency (assuming EUR for Netherlands)
            currency_field = self.driver.find_element(
                By.NAME, "currency"
            )
            currency_field.send_keys(data['campaign_details']['currency'])
            
            self.logger.info("Goal section filled")
            
        except Exception as e:
            self.logger.error(f"Failed to fill goal section: {e}")
            raise
    
    def upload_image(self, image_path):
        """Upload campaign image"""
        try:
            upload_input = self.driver.find_element(
                By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"
            )
            upload_input.send_keys(image_path)
            
            self.logger.info("Image uploaded")
            time.sleep(2)  # Wait for upload
            
        except Exception as e:
            self.logger.warning(f"Image upload failed: {e}")
    
    def submit_campaign(self):
        """Submit and publish campaign"""
        try:
            # Find submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Publish') or contains(text(), 'Submit')]")
                )
            )
            submit_button.click()
            
            # Wait for success message
            time.sleep(3)
            
            # Get campaign URL
            try:
                campaign_url = self.driver.current_url
                if "/fundraiser/" in campaign_url:
                    self.logger.info(f"Campaign created: {campaign_url}")
                    return campaign_url
            except:
                pass
            
            # Try to find success message
            success_element = self.driver.find_element(
                By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'created')]"
            )
            
            self.logger.info("Campaign submitted successfully")
            return "Campaign created (check dashboard for URL)"
            
        except Exception as e:
            self.logger.error(f"Submission failed: {e}")
            return None
    
    def process_from_csv(self, csv_path):
        """Process multiple campaigns from CSV"""
        import pandas as pd
        
        df = pd.read_csv(csv_path)
        results = []
        
        for _, row in df.iterrows():
            if pd.isna(row.get('whydonate_url')):
                try:
                    campaign_data = self.prepare_campaign_data(row)
                    url = self.create_campaign(campaign_data)
                    
                    if url:
                        results.append({
                            'campaign_id': row.get('campaign_id'),
                            'status': 'created',
                            'url': url
                        })
                    else:
                        results.append({
                            'campaign_id': row.get('campaign_id'),
                            'status': 'failed',
                            'error': 'Creation failed'
                        })
                except Exception as e:
                    results.append({
                        'campaign_id': row.get('campaign_id'),
                        'status': 'error',
                        'error': str(e)
                    })
        
        return results
    
    def prepare_campaign_data(self, row):
        """Prepare data dictionary for Whydonate"""
        return {
            'campaign_details': {
                'title': row.get('suggested_title', row.get('title', 'Untitled Campaign')),
                'description': row.get('clean_text', row.get('presentation_text', '')),
                'category': row.get('category', 'General'),
                'target_amount': float(row.get('target_amount', 1000)),
                'currency': 'EUR'
            },
            'organizer_details': {
                'name': row.get('name', ''),
                'email': row.get('email', ''),
                'phone': row.get('phone', '')
            },
            'campaign_image': row.get('campaign_image', '')
        }
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        self.logger.info("Browser closed")


# Flask API for Web Form Integration
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# In-memory storage (use database in production)
campaigns_db = []

@app.route('/api/submit-campaign', methods=['POST'])
def submit_campaign():
    """API endpoint for web form submission"""
    try:
        data = request.json
        
        # Generate campaign ID
        import uuid
        campaign_id = str(uuid.uuid4())[:8]
        
        # Prepare campaign data
        campaign = {
            'campaign_id': campaign_id,
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'title': data.get('campaign_title'),
            'presentation_text': data.get('presentation_text'),
            'category': data.get('category'),
            'target_amount': data.get('target_amount'),
            'donation_type': data.get('donation_type'),
            'tags': data.get('tags'),
            'status': 'pending',
            'created_date': data.get('timestamp'),
            'whydonate_url': None
        }
        
        # Save to CSV (append)
        import csv
        csv_path = Path.home() / "Desktop" / "campaigns_master.csv"
        
        with open(csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=campaign.keys())
            writer.writerow(campaign)
        
        # Generate WhatsApp message
        from deskagent_v1 import DeskAgentV1
        agent = DeskAgentV1()
        whatsapp_message = agent.draft_whatsapp_message(
            campaign['name'],
            campaign['title'],
            f"https://whydonate.com/campaign/{campaign_id}"
        )
        
        # Start bot processing in background thread
        thread = threading.Thread(
            target=process_campaign_background,
            args=(campaign,)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'whatsapp_message': whatsapp_message,
            'message': 'Campaign submitted successfully. We will process it shortly.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def process_campaign_background(campaign):
    """Background processing for campaign creation"""
    try:
        # Initialize bot
        bot = WhydonateBot(headless=True)
        
        # Load credentials from config
        import json
        config_path = Path.home() / "Desktop" / "config.txt"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Login
        if bot.login(
            config['whydonate']['username'],
            config['whydonate']['password']
        ):
            # Create campaign
            campaign_data = bot.prepare_campaign_data(campaign)
            url = bot.create_campaign(campaign_data)
            
            if url:
                # Update CSV with URL
                update_campaign_url(campaign['campaign_id'], url)
                
                # Send WhatsApp notification (optional)
                send_whatsapp_notification(campaign['phone'], url)
        
        bot.close()
        
    except Exception as e:
        print(f"Background processing error: {e}")

def update_campaign_url(campaign_id, url):
    """Update campaign URL in CSV"""
    import pandas as pd
    csv_path = Path.home() / "Desktop" / "campaigns_master.csv"
    
    df = pd.read_csv(csv_path)
    mask = df['campaign_id'] == campaign_id
    if mask.any():
        df.loc[mask, 'whydonate_url'] = url
        df.loc[mask, 'status'] = 'active'
        df.loc[mask, 'last_updated'] = pd.Timestamp.now()
        df.to_csv(csv_path, index=False)

def send_whatsapp_notification(phone, url):
    """Send WhatsApp notification (simplified)"""
    # In production, integrate with WhatsApp Business API
    print(f"Would send WhatsApp to {phone} with URL: {url}")

if __name__ == "__main__":
    # Run API server
    app.run(host='0.0.0.0', port=5000, debug=True)