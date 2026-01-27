#!/usr/bin/env python3
"""
DeskAgent v1 - Fundraising Campaign Manager
Automated Whydonate campaign creation with persistent sessions
"""

import sys
import pandas as pd
import json
import os
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Constants
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_DIR = DATA_DIR / ".csv"
PROFILE_DIR = DATA_DIR / "chrome_profile"
CSV_PATH = CSV_DIR / "campaigns_master.csv"
NOTES_PATH = DATA_DIR / "agent_notes.txt"
CONFIG_PATH = DATA_DIR / "config.txt"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


class CampaignManager:
    """Manages campaign data in CSV"""
    
    def __init__(self):
        self.csv_path = CSV_PATH
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV with proper structure if it doesn't exist"""
        if not self.csv_path.exists():
            columns = [
                'campaign_id', 'name', 'email', 'phone', 'title',
                'presentation_text', 'clean_text', 'suggested_title',
                'whatsapp_message', 'whydonate_url', 'status',
                'created_date', 'last_updated', 'category', 'target_amount',
                'donation_type', 'notes'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.csv_path, index=False)
    
    def load_campaigns(self):
        """Load all campaigns from CSV"""
        try:
            return pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    def save_campaigns(self, df):
        """Save campaigns to CSV"""
        try:
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def add_campaign(self, campaign_data):
        """Add a new campaign"""
        df = self.load_campaigns()
        
        # Generate ID if not provided
        if 'campaign_id' not in campaign_data or not campaign_data['campaign_id']:
            import uuid
            campaign_data['campaign_id'] = str(uuid.uuid4())[:8]
        
        # Set timestamps
        now = datetime.now()
        campaign_data['created_date'] = now.strftime("%Y-%m-%d")
        campaign_data['last_updated'] = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Set default status
        if 'status' not in campaign_data:
            campaign_data['status'] = 'draft'
        
        # Add to dataframe
        new_df = pd.concat([df, pd.DataFrame([campaign_data])], ignore_index=True)
        return self.save_campaigns(new_df)
    
    def update_campaign(self, campaign_id, updates):
        """Update a campaign"""
        df = self.load_campaigns()
        
        if campaign_id not in df['campaign_id'].values:
            return False
        
        # Apply updates
        for key, value in updates.items():
            df.loc[df['campaign_id'] == campaign_id, key] = value
        
        # Update timestamp
        df.loc[df['campaign_id'] == campaign_id, 'last_updated'] = \
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return self.save_campaigns(df)


class WhydonateAutomator:
    """Handles Whydonate automation with persistent profile"""
    
    def __init__(self):
        self.profile_dir = PROFILE_DIR
    
    def get_driver(self):
        """Get Chrome driver with persistent profile"""
        options = Options()
        options.add_argument(f"user-data-dir={self.profile_dir}")
        options.add_argument("profile-directory=Default")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        return webdriver.Chrome(options=options)
    
    def test_connection(self):
        """Test if we can access Whydonate"""
        driver = self.get_driver()
        try:
            driver.get("https://whydonate.com/en/dashboard")
            time.sleep(3)
            return "login" not in driver.current_url
        finally:
            driver.quit()
    
    def create_campaign(self, campaign_data):
        """
        Create a campaign on Whydonate
        Returns: (success, url_or_error)
        """
        driver = self.get_driver()
        
        try:
            # Navigate to create page
            driver.get("https://whydonate.com/en/fundraiser/create")
            time.sleep(5)
            
            # Fill form fields
            fields = [
                ('title', campaign_data.get('title', '')),
                ('category', campaign_data.get('category', 'General')),
                ('description', campaign_data.get('description', '')),
                ('goal_amount', str(campaign_data.get('target_amount', 1000)))
            ]
            
            for field_name, value in fields:
                if value:
                    self._fill_field(driver, field_name, value)
                    time.sleep(1)
            
            # Submit
            return self._submit_form(driver)
            
        except Exception as e:
            return False, str(e)
        finally:
            driver.quit()
    
    def _fill_field(self, driver, field_name, value):
        """Fill a form field"""
        try:
            # Try by name first
            element = driver.find_element(By.NAME, field_name)
            element.clear()
            element.send_keys(value)
        except:
            # Try other selectors
            selectors = [
                f"input[name='{field_name}']",
                f"textarea[name='{field_name}']",
                f"#{field_name}",
                f"[placeholder*='{field_name.title()}']"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    element.clear()
                    element.send_keys(value)
                    break
                except:
                    continue
    
    def _submit_form(self, driver):
        """Submit the form and return result"""
        # Look for submit button
        submit_texts = ['Publish', 'Create', 'Submit', 'Save']
        
        for text in submit_texts:
            try:
                button = driver.find_element(
                    By.XPATH, f"//button[contains(text(), '{text}')]"
                )
                if button.is_displayed():
                    button.click()
                    time.sleep(10)
                    
                    # Check if successful
                    if "/fundraiser/" in driver.current_url:
                        return True, driver.current_url
                    else:
                        return False, "Submission failed - not redirected"
            except:
                continue
        
        return False, "No submit button found"


class TextProcessor:
    """Processes campaign text"""
    
    @staticmethod
    def clean_text(text):
        """Clean and format campaign text"""
        if not text or pd.isna(text):
            return ""
        
        # Basic cleaning
        text = ' '.join(str(text).split())  # Remove extra whitespace
        text = text.strip()
        
        # Ensure proper punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
    @staticmethod
    def suggest_title(name, text):
        """Generate title suggestions"""
        import random
        
        base_titles = [
            f"Support {name}'s Cause",
            f"{name}'s Fundraising Campaign",
            f"Help {name} Make a Difference",
            f"Join {name}'s Mission"
        ]
        
        return random.choice(base_titles)
    
    @staticmethod
    def generate_whatsapp_message(name, title, url, template="standard"):
        """Generate WhatsApp message"""
        templates = {
            "standard": f"""🌟 *{title}*

Hi! I'm {name}. I've started a fundraising campaign and would appreciate your support!

🔗 Campaign: {url}

Thank you for considering!
- {name}""",
            
            "urgent": f"""🚨 *URGENT: {title}*

Hello, I'm {name}. We urgently need your help with our campaign.

🔗 Please support: {url}

Every contribution counts!
- {name}""",
            
            "thank_you": f"""🙏 *Thank You!*

This is {name}. Thank you for considering our campaign: {title}

🔗 Learn more: {url}

With gratitude,
{name}"""
        }
        
        return templates.get(template, templates["standard"])


class DeskAgentGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.campaign_manager = CampaignManager()
        self.automator = WhydonateAutomator()
        self.text_processor = TextProcessor()
        
        self.root = tk.Tk()
        self.root.title("DeskAgent v1")
        self.root.geometry("1100x700")
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_campaigns_tab()
        self._create_automation_tab()
        self._create_whatsapp_tab()
        
        # Status bar
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def _create_campaigns_tab(self):
        """Create campaigns management tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Campaigns")
        
        # Campaign list
        frame = ttk.LabelFrame(tab, text="Campaign List", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('ID', 'Name', 'Title', 'Status', 'URL')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add New", 
                  command=self._add_campaign).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", 
                  command=self._load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clean Text", 
                  command=self._clean_selected).pack(side=tk.LEFT, padx=5)
    
    def _create_automation_tab(self):
        """Create Whydonate automation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Whydonate")
        
        # Status frame
        status_frame = ttk.LabelFrame(tab, text="Status", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.connection_label = ttk.Label(status_frame, text="Not tested")
        self.connection_label.pack(anchor=tk.W)
        
        # Instructions
        instr_frame = ttk.LabelFrame(tab, text="Instructions", padding="10")
        instr_frame.pack(fill=tk.X, padx=10, pady=5)
        
        instr_text = """1. First, manually login to Whydonate with VPN
2. Use 'Test Connection' to verify
3. Select campaigns to create
4. Campaigns will be created automatically"""
        
        ttk.Label(instr_frame, text=instr_text).pack(anchor=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Test Connection", 
                  command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Create Selected", 
                  command=self._create_selected).pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(tab, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
    
    def _create_whatsapp_tab(self):
        """Create WhatsApp message tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="WhatsApp")
        
        # Message display
        frame = ttk.LabelFrame(tab, text="Message", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.message_display = scrolledtext.ScrolledText(frame, height=20)
        self.message_display.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Generate", 
                  command=self._generate_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Copy", 
                  command=self._copy_message).pack(side=tk.LEFT, padx=5)
    
    def _load_data(self):
        """Load campaigns into treeview"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            df = self.campaign_manager.load_campaigns()
            
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=(
                    row.get('campaign_id', ''),
                    row.get('name', ''),
                    row.get('title', ''),
                    row.get('status', 'draft'),
                    row.get('whydonate_url', 'Not created')
                ))
            
            self._update_status(f"Loaded {len(df)} campaigns")
            
        except Exception as e:
            self._show_error(f"Failed to load data: {e}")
    
    def _add_campaign(self):
        """Add new campaign dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Campaign")
        dialog.geometry("500x400")
        
        # Simple form
        fields = [
            ('name', 'Name', tk.Entry(dialog, width=40)),
            ('title', 'Title', tk.Entry(dialog, width=40)),
            ('email', 'Email', tk.Entry(dialog, width=40)),
            ('phone', 'Phone', tk.Entry(dialog, width=40)),
            ('text', 'Story', scrolledtext.ScrolledText(dialog, height=8, width=40))
        ]
        
        entries = {}
        
        for i, (field, label, widget) in enumerate(fields):
            ttk.Label(dialog, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            widget.grid(row=i, column=1, padx=10, pady=5, sticky='w')
            entries[field] = widget
        
        # Save button
        def save():
            try:
                campaign_data = {
                    'name': entries['name'].get(),
                    'title': entries['title'].get(),
                    'email': entries['email'].get(),
                    'phone': entries['phone'].get(),
                    'presentation_text': entries['text'].get(1.0, tk.END).strip(),
                    'status': 'draft'
                }
                
                if self.campaign_manager.add_campaign(campaign_data):
                    self._update_status("Campaign added")
                    self._load_data()
                    dialog.destroy()
                else:
                    self._show_error("Failed to add campaign")
                    
            except Exception as e:
                self._show_error(f"Error: {e}")
        
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=1, pady=10)
    
    def _test_connection(self):
        """Test Whydonate connection"""
        self._update_status("Testing connection...")
        self.progress.start()
        
        try:
            connected = self.automator.test_connection()
            
            if connected:
                self.connection_label.config(text="✅ Connected to Whydonate")
                self._update_status("Connection successful")
            else:
                self.connection_label.config(text="❌ Not connected")
                self._update_status("Connection failed - check VPN/login")
                
        except Exception as e:
            self.connection_label.config(text="❌ Error testing connection")
            self._show_error(f"Connection test failed: {e}")
        finally:
            self.progress.stop()
    
    def _create_selected(self):
        """Create selected campaign on Whydonate"""
        selection = self.tree.selection()
        if not selection:
            self._show_warning("Select a campaign first")
            return
        
        item = self.tree.item(selection[0])
        campaign_id = item['values'][0]
        
        self._update_status(f"Creating campaign {campaign_id}...")
        self.progress.start()
        
        try:
            df = self.campaign_manager.load_campaigns()
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            campaign_data = {
                'title': campaign.get('title', ''),
                'description': campaign.get('clean_text', campaign.get('presentation_text', '')),
                'category': campaign.get('category', 'General'),
                'target_amount': float(campaign.get('target_amount', 1000))
            }
            
            success, result = self.automator.create_campaign(campaign_data)
            
            if success:
                # Update with URL
                self.campaign_manager.update_campaign(campaign_id, {
                    'whydonate_url': result,
                    'status': 'active'
                })
                
                self._update_status(f"Campaign created: {result}")
                self._load_data()
                self._show_info("Campaign created successfully!")
            else:
                self._update_status(f"Creation failed: {result}")
                self._show_error(f"Failed to create campaign: {result}")
                
        except Exception as e:
            self._show_error(f"Error: {e}")
        finally:
            self.progress.stop()
    
    def _clean_selected(self):
        """Clean text of selected campaign"""
        selection = self.tree.selection()
        if not selection:
            self._show_warning("Select a campaign first")
            return
        
        item = self.tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = self.campaign_manager.load_campaigns()
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            text = campaign.get('presentation_text', '')
            if pd.isna(text) or not text:
                self._show_warning("No text to clean")
                return
            
            cleaned = self.text_processor.clean_text(text)
            suggested = self.text_processor.suggest_title(
                campaign.get('name', ''), cleaned
            )
            
            # Update
            self.campaign_manager.update_campaign(campaign_id, {
                'clean_text': cleaned,
                'suggested_title': suggested
            })
            
            self._update_status("Text cleaned")
            self._load_data()
            
        except Exception as e:
            self._show_error(f"Error cleaning text: {e}")
    
    def _generate_message(self):
        """Generate WhatsApp message"""
        selection = self.tree.selection()
        if not selection:
            self._show_warning("Select a campaign first")
            return
        
        item = self.tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = self.campaign_manager.load_campaigns()
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            name = campaign.get('name', '')
            title = campaign.get('title', '')
            url = campaign.get('whydonate_url', '')
            
            if not url or pd.isna(url):
                self._show_warning("Create campaign on Whydonate first")
                return
            
            message = self.text_processor.generate_whatsapp_message(
                name, title, url
            )
            
            self.message_display.delete(1.0, tk.END)
            self.message_display.insert(1.0, message)
            
        except Exception as e:
            self._show_error(f"Error generating message: {e}")
    
    def _copy_message(self):
        """Copy message to clipboard"""
        message = self.message_display.get(1.0, tk.END).strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self._update_status("Message copied to clipboard")
    
    def _update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def _show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self._update_status(f"Error: {message}")
    
    def _show_warning(self, message):
        """Show warning message"""
        messagebox.showwarning("Warning", message)
        self._update_status(f"Warning: {message}")
    
    def _show_info(self, message):
        """Show info message"""
        messagebox.showinfo("Information", message)
        self._update_status(message)
    
    def run(self):
        """Run the application"""
        self._update_status("DeskAgent v1 Ready")
        self.root.mainloop()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("DeskAgent v1 - Fundraising Campaign Manager")
    print("="*60)
    print(f"Data directory: {DATA_DIR}")
    print(f"CSV file: {CSV_PATH}")
    print(f"Chrome profile: {PROFILE_DIR}")
    print("="*60)
    
    app = DeskAgentGUI()
    app.run()


if __name__ == "__main__":
    main()