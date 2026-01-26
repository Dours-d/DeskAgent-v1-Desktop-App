from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import logging
import sys 
from pathlib import Path

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent


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

# scripts/whydonate_bot.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import logging
import sys 
from pathlib import Path

# Get base directory - THIS SHOULD BE AT THE TOP
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

print(f"[DEBUG] BASE_DIR: {BASE_DIR}")  # Debug line


class WhydonateBot:
    def __init__(self, headless=True):
        self.base_dir = BASE_DIR  # Store BASE_DIR as instance variable
        self.setup_logging()
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        
    def setup_logging(self):
        """Setup logging with correct file path"""
        log_path = self.base_dir / "data" / "logs" / "whydonate_bot.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)  # Create logs directory
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_path)),  # Use absolute path
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized WhydonateBot. Base directory: {self.base_dir}")
    
    def setup_driver(self, headless):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        # For ChromeDriver - make sure you have ChromeDriver installed
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise
    
    def get_config_path(self):
        """Get the correct config file path"""
        config_path = self.base_dir / "data" / "config.txt"
        self.logger.info(f"Looking for config at: {config_path}")
        return config_path
    
    def get_csv_path(self):
        """Get the correct CSV file path"""
        csv_path = self.base_dir / "data" / ".csv" / "campaigns_master.csv"
        self.logger.info(f"Looking for CSV at: {csv_path}")
        return csv_path
    
    def load_config(self):
        """Load configuration from file"""
        config_path = self.get_config_path()
        try:
            if not config_path.exists():
                self.logger.error(f"Config file not found at: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return None
    
    def load_campaigns_from_csv(self):
        """Load campaigns from CSV"""
        csv_path = self.get_csv_path()
        try:
            if not csv_path.exists():
                self.logger.error(f"CSV file not found at: {csv_path}")
                return pd.DataFrame()
            
            df = pd.read_csv(csv_path, encoding='utf-8')
            self.logger.info(f"Loaded {len(df)} campaigns from CSV")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    def update_campaign_in_csv(self, campaign_id, updates):
        """Update campaign in CSV"""
        import pandas as pd
        csv_path = self.get_csv_path()
        
        try:
            if not csv_path.exists():
                self.logger.error(f"CSV file not found at: {csv_path}")
                return False
            
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Find campaign
            mask = df['campaign_id'] == campaign_id
            if not mask.any():
                self.logger.error(f"Campaign {campaign_id} not found in CSV")
                return False
            
            # Apply updates
            for key, value in updates.items():
                df.loc[mask, key] = value
            
            # Update timestamp
            from datetime import datetime
            df.loc[mask, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            self.logger.info(f"Updated campaign {campaign_id} in CSV")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating CSV: {e}")
            return False
    
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
            upload_input.send_keys(str(image_path))
            
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
            try:
                success_element = self.driver.find_element(
                    By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'created')]"
                )
                self.logger.info("Campaign submitted successfully")
                return "Campaign created (check dashboard for URL)"
            except:
                pass
            
            # If no success element found, check for errors
            try:
                error_elements = self.driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error')]"
                )
                if error_elements:
                    errors = [e.text for e in error_elements[:3]]
                    self.logger.error(f"Submission errors: {errors}")
                    return None
            except:
                pass
            
            # Default return
            self.logger.warning("Could not determine submission status")
            return None
            
        except Exception as e:
            self.logger.error(f"Submission failed: {e}")
            return None
    
    def process_pending_campaigns(self):
        """Process all pending campaigns from CSV"""
        import pandas as pd
        
        try:
            df = self.load_campaigns_from_csv()
            if df.empty:
                self.logger.warning("No campaigns found in CSV")
                return []
            
            # Filter campaigns that need processing
            pending_campaigns = df[
                (df['status'].isin(['pending', 'draft'])) & 
                (df['whydonate_url'].isna())
            ]
            
            if pending_campaigns.empty:
                self.logger.info("No pending campaigns to process")
                return []
            
            self.logger.info(f"Found {len(pending_campaigns)} pending campaigns")
            
            # Load config for credentials
            config = self.load_config()
            if not config:
                self.logger.error("Cannot process campaigns without config")
                return []
            
            # Login
            username = config.get('whydonate', {}).get('username', '')
            password = config.get('whydonate', {}).get('password', '')
            
            if not username or not password:
                self.logger.error("Whydonate credentials not found in config")
                return []
            
            if not self.login(username, password):
                self.logger.error("Login failed, cannot process campaigns")
                return []
            
            # Process each campaign
            results = []
            for _, row in pending_campaigns.iterrows():
                try:
                    campaign_id = row.get('campaign_id')
                    self.logger.info(f"Processing campaign: {campaign_id}")
                    
                    campaign_data = self.prepare_campaign_data(row)
                    url = self.create_campaign(campaign_data)
                    
                    if url:
                        # Update CSV with URL
                        updates = {
                            'whydonate_url': url,
                            'status': 'active',
                            'last_updated': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        if self.update_campaign_in_csv(campaign_id, updates):
                            results.append({
                                'campaign_id': campaign_id,
                                'status': 'created',
                                'url': url,
                                'name': row.get('name', 'Unknown')
                            })
                        else:
                            results.append({
                                'campaign_id': campaign_id,
                                'status': 'csv_update_failed',
                                'error': 'Failed to update CSV'
                            })
                    else:
                        results.append({
                            'campaign_id': campaign_id,
                            'status': 'creation_failed',
                            'error': 'Failed to create campaign on Whydonate'
                        })
                        
                except Exception as e:
                    self.logger.error(f"Error processing campaign {row.get('campaign_id')}: {e}")
                    results.append({
                        'campaign_id': row.get('campaign_id'),
                        'status': 'error',
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing pending campaigns: {e}")
            return []
    
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
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.logger.info("Browser closed")


# Flask API for Web Form Integration
from flask import Flask, request, jsonify
import threading
from datetime import datetime

app = Flask(__name__)

@app.route('/api/submit-campaign', methods=['POST'])
def submit_campaign():
    """API endpoint for web form submission"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'campaign_title', 'presentation_text']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
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
            'suggested_title': data.get('campaign_title'),  # Use provided title as suggested
            'presentation_text': data.get('presentation_text'),
            'category': data.get('category', 'General'),
            'target_amount': data.get('target_amount', 1000),
            'donation_type': data.get('donation_type', 'one-time'),
            'tags': data.get('tags', ''),
            'status': 'pending',
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'whydonate_url': None,
            'clean_text': None,
            'whatsapp_message': None
        }
        
        # Get CSV path using BASE_DIR
        csv_path = BASE_DIR / "data" / ".csv" / "campaigns_master.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        
        # Save to CSV
        import pandas as pd
        import os
        
        # Check if file exists and has data
        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path, encoding='utf-8')
                new_df = pd.concat([existing_df, pd.DataFrame([campaign])], ignore_index=True)
            except:
                # If error reading existing file, create new
                new_df = pd.DataFrame([campaign])
        else:
            new_df = pd.DataFrame([campaign])
        
        # Save CSV
        new_df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Import DeskAgent to generate WhatsApp message
        try:
            # Add scripts directory to path
            scripts_dir = BASE_DIR / "scripts"
            sys.path.append(str(scripts_dir))
            
            from deskagent_v1 import DeskAgentV1
            agent = DeskAgentV1()
            whatsapp_message = agent.draft_whatsapp_message(
                campaign['name'],
                campaign['title'],
                f"https://whydonate.com/campaign/{campaign_id}"
            )
        except ImportError as e:
            whatsapp_message = f"🌟 *{campaign['title']}*\n\nHi! I'm {campaign['name']} and I've started a fundraising campaign. Your support would mean the world to us!\n\n🔗 Campaign will be available soon!"
        
        # Start background processing
        thread = threading.Thread(
            target=process_campaign_background,
            args=(campaign_id,)
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
        app.logger.error(f"API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def process_campaign_background(campaign_id):
    """Background processing for campaign creation"""
    import time
    
    try:
        print(f"[BACKGROUND] Processing campaign: {campaign_id}")
        
        # Wait a moment to ensure CSV is written
        time.sleep(2)
        
        # Initialize bot
        bot = WhydonateBot(headless=True)
        
        # Process pending campaigns
        results = bot.process_pending_campaigns()
        
        # Find our campaign in results
        for result in results:
            if result.get('campaign_id') == campaign_id:
                print(f"[BACKGROUND] Campaign {campaign_id} processed: {result.get('status')}")
                if result.get('url'):
                    print(f"[BACKGROUND] Campaign URL: {result.get('url')}")
                break
        
        bot.close()
        
    except Exception as e:
        print(f"[BACKGROUND] Error processing campaign {campaign_id}: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DeskAgent Whydonate Bot',
        'base_dir': str(BASE_DIR),
        'csv_exists': (BASE_DIR / "data" / ".csv" / "campaigns_master.csv").exists(),
        'config_exists': (BASE_DIR / "data" / "config.txt").exists()
    })


@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get list of campaigns"""
    try:
        csv_path = BASE_DIR / "data" / ".csv" / "campaigns_master.csv"
        
        if not csv_path.exists():
            return jsonify({'campaigns': [], 'count': 0})
        
        import pandas as pd
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        campaigns = df.to_dict('records')
        return jsonify({
            'campaigns': campaigns,
            'count': len(campaigns)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'campaigns': []
        }), 500


if __name__ == "__main__":
    print(f"Starting Whydonate Bot API...")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"CSV Path: {BASE_DIR / 'data' / '.csv' / 'campaigns_master.csv'}")
    
    # Create necessary directories
    (BASE_DIR / "data" / "logs").mkdir(parents=True, exist_ok=True)
    
    # Run API server
    app.run(host='0.0.0.0', port=5000, debug=True)