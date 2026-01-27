import sys
import pandas as pd
import json
import os
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Get base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

class DeskAgentV1:
    def __init__(self):
        self.base_dir = BASE_DIR
        self.data_dir = self.base_dir / "data"
        self.csv_dir = self.data_dir / ".csv"
        self.profile_dir = self.data_dir / "chrome_profile"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.csv_path = self.csv_dir / "campaigns_master.csv"
        self.notes_path = self.data_dir / "agent_notes.txt"
        self.config_path = self.data_dir / "config.txt"
        
        self.initialize_files()
    
    def initialize_files(self):
        """Initialize required files"""
        # CSV file
        if not self.csv_path.exists():
            columns = [
                'campaign_id', 'name', 'email', 'phone', 'title',
                'presentation_text', 'clean_text', 'suggested_title',
                'whatsapp_message', 'whydonate_url', 'status',
                'created_date', 'last_updated', 'category', 'target_amount',
                'campaign_image', 'tags', 'donation_type'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.csv_path, index=False)
        
        # Notes file
        if not self.notes_path.exists():
            with open(self.notes_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("DeskAgent v1 - Agent Notes\n")
                f.write("=" * 60 + "\n")
    
    def get_chrome_driver(self):
        """Get Chrome driver with persistent profile"""
        options = Options()
        options.add_argument(f"user-data-dir={self.profile_dir}")
        options.add_argument("profile-directory=Default")
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        return webdriver.Chrome(options=options)
    
    def create_whydonate_campaign(self, campaign_data):
        """Create a campaign on Whydonate using logged-in session"""
        driver = self.get_chrome_driver()
        
        try:
            # Navigate to create page
            print("Navigating to campaign creation page...")
            driver.get("https://whydonate.com/en/fundraiser/create")
            time.sleep(5)
            
            # Check if we're on the right page
            if "create" not in driver.current_url:
                print(f"Warning: Not on create page. Current URL: {driver.current_url}")
                # Try alternative URL
                driver.get("https://whydonate.com/fundraiser/create")
                time.sleep(5)
            
            # Take screenshot for debugging
            driver.save_screenshot(str(self.data_dir / "create_page_start.png"))
            
            # Fill the form step by step
            print("Filling campaign form...")
            
            # 1. Campaign Title
            try:
                title_field = driver.find_element(By.NAME, "title")
                title_field.clear()
                title_field.send_keys(campaign_data.get('title', ''))
                print("✓ Title filled")
            except:
                print("Could not find title field")
            
            time.sleep(1)
            
            # 2. Category
            try:
                category_select = driver.find_element(By.NAME, "category")
                category = campaign_data.get('category', 'General')
                category_select.send_keys(category)
                print(f"✓ Category set: {category}")
            except:
                print("Could not find category field")
            
            time.sleep(1)
            
            # 3. Description (using JavaScript for rich text editor)
            description = campaign_data.get('description', '')
            if description:
                try:
                    # Try to find and fill description field
                    driver.execute_script(f"""
                        // Try multiple ways to set description
                        var editor = document.querySelector('[contenteditable="true"]');
                        if (editor) {{
                            editor.innerHTML = '{description}';
                        }} else {{
                            var textarea = document.querySelector('textarea[name="description"]');
                            if (textarea) {{
                                textarea.value = '{description}';
                            }}
                        }}
                    """)
                    print("✓ Description filled")
                except:
                    print("Could not fill description")
            
            time.sleep(1)
            
            # 4. Target Amount
            try:
                amount_field = driver.find_element(By.NAME, "goal_amount")
                amount_field.clear()
                amount_field.send_keys(str(campaign_data.get('target_amount', 1000)))
                print(f"✓ Target amount set: {campaign_data.get('target_amount', 1000)}")
            except:
                print("Could not find target amount field")
            
            time.sleep(1)
            
            # Take screenshot before submission
            driver.save_screenshot(str(self.data_dir / "create_page_filled.png"))
            
            # 5. Submit the form
            print("Submitting campaign...")
            try:
                # Look for submit button
                submit_buttons = driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Publish') or contains(text(), 'Create') or contains(text(), 'Submit')]"
                )
                
                if submit_buttons:
                    submit_buttons[0].click()
                    print("✓ Submit button clicked")
                else:
                    # Try JavaScript submission
                    driver.execute_script("""
                        var forms = document.getElementsByTagName('form');
                        if (forms.length > 0) {
                            forms[0].submit();
                        }
                    """)
                    print("✓ Form submitted via JavaScript")
                
                # Wait for submission
                time.sleep(10)
                
                # Take screenshot after submission
                driver.save_screenshot(str(self.data_dir / "create_page_submitted.png"))
                
                # Get the final URL (campaign URL if successful)
                campaign_url = driver.current_url
                print(f"Final URL: {campaign_url}")
                
                # Check if creation was successful
                if "/fundraiser/" in campaign_url or "/campaign/" in campaign_url:
                    print(f"🎉 Campaign created successfully!")
                    print(f"URL: {campaign_url}")
                    return campaign_url
                else:
                    print("⚠️ May still be on create page")
                    return None
                
            except Exception as e:
                print(f"Error submitting: {e}")
                return None
            
        except Exception as e:
            print(f"Error creating campaign: {e}")
            return None
            
        finally:
            driver.quit()
    
    def process_campaigns_to_whydonate(self):
        """Process all campaigns from CSV and create on Whydonate"""
        try:
            # Read CSV
            df = pd.read_csv(self.csv_path)
            
            # Filter campaigns that need to be created
            pending_campaigns = df[
                (df['whydonate_url'].isna()) & 
                (df['status'].isin(['pending', 'draft']))
            ]
            
            if pending_campaigns.empty:
                print("No pending campaigns to process")
                return []
            
            results = []
            
            for idx, row in pending_campaigns.iterrows():
                campaign_id = row.get('campaign_id', f'camp_{idx}')
                print(f"\nProcessing campaign: {campaign_id}")
                
                # Prepare campaign data
                campaign_data = {
                    'title': row.get('suggested_title', row.get('title', '')),
                    'description': row.get('clean_text', row.get('presentation_text', '')),
                    'category': row.get('category', 'General'),
                    'target_amount': float(row.get('target_amount', 1000))
                }
                
                # Create campaign on Whydonate
                campaign_url = self.create_whydonate_campaign(campaign_data)
                
                if campaign_url:
                    # Update CSV
                    df.loc[df['campaign_id'] == campaign_id, 'whydonate_url'] = campaign_url
                    df.loc[df['campaign_id'] == campaign_id, 'status'] = 'active'
                    df.loc[df['campaign_id'] == campaign_id, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    results.append({
                        'campaign_id': campaign_id,
                        'status': 'created',
                        'url': campaign_url
                    })
                    
                    print(f"✓ Campaign {campaign_id} created: {campaign_url}")
                else:
                    results.append({
                        'campaign_id': campaign_id,
                        'status': 'failed',
                        'error': 'Creation failed'
                    })
                    
                    print(f"✗ Campaign {campaign_id} creation failed")
            
            # Save updated CSV
            df.to_csv(self.csv_path, index=False)
            
            return results
            
        except Exception as e:
            print(f"Error processing campaigns: {e}")
            return []
    
    # ... [Previous methods for text cleaning, WhatsApp generation, etc.] ...
    # Add all your existing methods here

class DeskAgentGUI:
    def __init__(self):
        self.agent = DeskAgentV1()
        self.root = tk.Tk()
        self.root.title("DeskAgent v1 - Complete System")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        self.load_campaigns()
    
    def setup_ui(self):
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Campaign Management
        self.campaign_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.campaign_tab, text="Campaigns")
        self.setup_campaign_tab()
        
        # Tab 2: Whydonate Automation
        self.automation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.automation_tab, text="Whydonate Automation")
        self.setup_automation_tab()
        
        # Tab 3: WhatsApp Messages
        self.whatsapp_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.whatsapp_tab, text="WhatsApp")
        self.setup_whatsapp_tab()
    
    def setup_campaign_tab(self):
        # Campaign list frame
        list_frame = ttk.LabelFrame(self.campaign_tab, text="Campaign List", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for campaigns
        columns = ('ID', 'Name', 'Title', 'Status', 'Whydonate URL')
        self.campaign_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.campaign_tree.heading(col, text=col)
            self.campaign_tree.column(col, width=150)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.campaign_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.campaign_tree.xview)
        self.campaign_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout
        self.campaign_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self.campaign_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.load_campaigns).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Campaign", command=self.add_campaign).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Process Text", command=self.process_text).pack(side=tk.LEFT, padx=5)
    
    def setup_automation_tab(self):
        """Setup Whydonate automation tab"""
        frame = ttk.Frame(self.automation_tab, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(frame, text="🎯 Whydonate Automation", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(frame, text="Status:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.status_label = ttk.Label(frame, text="Ready", foreground="green")
        self.status_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Profile status
        profile_status = "✅ Configured" if self.agent.profile_dir.exists() else "❌ Not configured"
        ttk.Label(frame, text=f"Chrome Profile: {profile_status}").pack(anchor=tk.W, pady=(0, 10))
        
        # Instructions
        instructions = """
        Instructions:
        1. Make sure you've logged into Whydonate manually at least once
        2. The system will use your saved Chrome profile
        3. Select campaigns to create on Whydonate
        4. Campaigns will be created automatically
        
        Note: You need to be connected to VPN (Netherlands) when running this.
        """
        
        ttk.Label(frame, text=instructions, justify=tk.LEFT).pack(fill=tk.X, pady=(0, 20))
        
        # Control buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Test Whydonate Access", 
                  command=self.test_whydonate_access).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Selected Campaign", 
                  command=self.create_selected_campaign).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create All Pending", 
                  command=self.create_all_pending).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=300)
        self.progress.pack(pady=20)
        
        # Results text
        ttk.Label(frame, text="Results:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.results_text = scrolledtext.ScrolledText(frame, height=10, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_whatsapp_tab(self):
        """Setup WhatsApp message tab"""
        frame = ttk.Frame(self.whatsapp_tab, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📱 WhatsApp Message Generator", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Template selection
        template_frame = ttk.Frame(frame)
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT, padx=(0, 10))
        self.template_var = tk.StringVar(value="standard")
        ttk.Combobox(template_frame, textvariable=self.template_var, 
                    values=["standard", "urgent", "thank_you"], width=15).pack(side=tk.LEFT)
        
        # Message display
        self.whatsapp_display = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD)
        self.whatsapp_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Generate for Selected", 
                  command=self.generate_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy to Clipboard", 
                  command=self.copy_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to Campaign", 
                  command=self.save_whatsapp).pack(side=tk.LEFT, padx=5)
    
    def load_campaigns(self):
        """Load campaigns from CSV into treeview"""
        # Clear existing items
        for item in self.campaign_tree.get_children():
            self.campaign_tree.delete(item)
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            
            for _, row in df.iterrows():
                self.campaign_tree.insert('', 'end', values=(
                    row.get('campaign_id', ''),
                    row.get('name', ''),
                    row.get('title', ''),
                    row.get('status', 'draft'),
                    row.get('whydonate_url', 'Not created')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load campaigns: {e}")
    
    def test_whydonate_access(self):
        """Test if we can access Whydonate with current profile"""
        self.status_label.config(text="Testing access...", foreground="orange")
        self.root.update()
        
        try:
            driver = self.agent.get_chrome_driver()
            driver.get("https://whydonate.com/en/dashboard")
            time.sleep(3)
            
            if "login" not in driver.current_url:
                self.status_label.config(text="✅ Access successful! Logged in.", foreground="green")
                messagebox.showinfo("Success", "Whydonate access successful! You are logged in.")
            else:
                self.status_label.config(text="❌ Not logged in", foreground="red")
                messagebox.showwarning("Warning", "Not logged in to Whydonate. Please login manually first.")
            
            driver.quit()
            
        except Exception as e:
            self.status_label.config(text="❌ Error testing access", foreground="red")
            messagebox.showerror("Error", f"Failed to test access: {e}")
    
    def create_selected_campaign(self):
        """Create selected campaign on Whydonate"""
        selection = self.campaign_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        # Get campaign data
        try:
            df = pd.read_csv(self.agent.csv_path)
            campaign_row = df[df['campaign_id'] == campaign_id].iloc[0]
            
            campaign_data = {
                'title': campaign_row.get('suggested_title', campaign_row.get('title', '')),
                'description': campaign_row.get('clean_text', campaign_row.get('presentation_text', '')),
                'category': campaign_row.get('category', 'General'),
                'target_amount': float(campaign_row.get('target_amount', 1000))
            }
            
            self.status_label.config(text="Creating campaign...", foreground="orange")
            self.progress.start()
            self.root.update()
            
            # Create campaign
            url = self.agent.create_whydonate_campaign(campaign_data)
            
            if url:
                # Update CSV
                df.loc[df['campaign_id'] == campaign_id, 'whydonate_url'] = url
                df.loc[df['campaign_id'] == campaign_id, 'status'] = 'active'
                df.to_csv(self.agent.csv_path, index=False)
                
                self.status_label.config(text="✅ Campaign created!", foreground="green")
                self.results_text.insert(tk.END, f"✓ {campaign_id}: {url}\n")
                messagebox.showinfo("Success", f"Campaign created successfully!\nURL: {url}")
                
                # Refresh list
                self.load_campaigns()
            else:
                self.status_label.config(text="❌ Creation failed", foreground="red")
                messagebox.showerror("Error", "Failed to create campaign")
            
        except Exception as e:
            self.status_label.config(text="❌ Error", foreground="red")
            messagebox.showerror("Error", f"Failed to create campaign: {e}")
        
        finally:
            self.progress.stop()
    
    def create_all_pending(self):
        """Create all pending campaigns"""
        try:
            df = pd.read_csv(self.agent.csv_path)
            pending = df[df['whydonate_url'].isna()]
            
            if pending.empty:
                messagebox.showinfo("Info", "No pending campaigns to create")
                return
            
            response = messagebox.askyesno("Confirm", f"Create {len(pending)} pending campaigns?")
            if not response:
                return
            
            self.status_label.config(text=f"Creating {len(pending)} campaigns...", foreground="orange")
            self.progress.start()
            self.results_text.delete(1.0, tk.END)
            self.root.update()
            
            results = self.agent.process_campaigns_to_whydonate()
            
            # Display results
            success_count = sum(1 for r in results if r['status'] == 'created')
            self.results_text.insert(tk.END, f"\nResults: {success_count}/{len(pending)} successful\n")
            
            for result in results:
                if result['status'] == 'created':
                    self.results_text.insert(tk.END, f"✓ {result['campaign_id']}: {result['url']}\n")
                else:
                    self.results_text.insert(tk.END, f"✗ {result['campaign_id']}: Failed\n")
            
            self.status_label.config(text=f"✅ {success_count}/{len(pending)} created", foreground="green")
            
            # Refresh list
            self.load_campaigns()
            
        except Exception as e:
            self.status_label.config(text="❌ Error", foreground="red")
            messagebox.showerror("Error", f"Failed to create campaigns: {e}")
        
        finally:
            self.progress.stop()
    
    def generate_whatsapp(self):
        """Generate WhatsApp message for selected campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            name = campaign.get('name', '')
            title = campaign.get('title', '')
            url = campaign.get('whydonate_url', '')
            
            if not url or pd.isna(url):
                messagebox.showwarning("Warning", "Campaign not created on Whydonate yet")
                return
            
            # Generate message
            template = self.template_var.get()
            message = f"🌟 *{title}*\n\nHi! I'm {name}."
            
            if template == "urgent":
                message += f"\n\nI urgently need your support for my campaign!\n\n🔗 {url}"
            elif template == "thank_you":
                message += f"\n\nThank you for considering my campaign!\n\n🔗 {url}"
            else:
                message += f"\n\nI've started a fundraising campaign and would appreciate your support!\n\n🔗 {url}"
            
            message += f"\n\nThank you!\n{name}"
            
            self.whatsapp_display.delete(1.0, tk.END)
            self.whatsapp_display.insert(1.0, message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate message: {e}")
    
    def copy_whatsapp(self):
        """Copy WhatsApp message to clipboard"""
        message = self.whatsapp_display.get(1.0, tk.END).strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            messagebox.showinfo("Copied", "Message copied to clipboard!")
    
    def save_whatsapp(self):
        """Save WhatsApp message to campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        message = self.whatsapp_display.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "No message to save")
            return
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            df.loc[df['campaign_id'] == campaign_id, 'whatsapp_message'] = message
            df.to_csv(self.agent.csv_path, index=False)
            
            messagebox.showinfo("Saved", "WhatsApp message saved to campaign!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save message: {e}")
    
    def add_campaign(self):
        """Add new campaign dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Campaign")
        dialog.geometry("500x400")
        
        # Form fields
        fields = [
            ('name', 'Name'),
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('title', 'Campaign Title'),
            ('category', 'Category'),
            ('target_amount', 'Target Amount (€)'),
            ('presentation_text', 'Story')
        ]
        
        entries = {}
        
        for i, (field, label) in enumerate(fields):
            ttk.Label(dialog, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            if field == 'presentation_text':
                entry = scrolledtext.ScrolledText(dialog, height=8, width=40)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky='nsew')
            else:
                entry = ttk.Entry(dialog, width=40)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky='w')
            
            entries[field] = entry
        
        # Configure grid weights
        dialog.grid_rowconfigure(len(fields), weight=1)
        dialog.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        def save_campaign():
            try:
                campaign_data = {}
                for field, entry in entries.items():
                    if field == 'presentation_text':
                        campaign_data[field] = entry.get(1.0, tk.END).strip()
                    else:
                        campaign_data[field] = entry.get().strip()
                
                # Generate campaign ID
                import uuid
                campaign_id = str(uuid.uuid4())[:8]
                
                # Add to CSV
                df = pd.read_csv(self.agent.csv_path)
                
                new_row = {
                    'campaign_id': campaign_id,
                    'name': campaign_data.get('name', ''),
                    'email': campaign_data.get('email', ''),
                    'phone': campaign_data.get('phone', ''),
                    'title': campaign_data.get('title', ''),
                    'presentation_text': campaign_data.get('presentation_text', ''),
                    'category': campaign_data.get('category', 'General'),
                    'target_amount': float(campaign_data.get('target_amount', 1000)),
                    'status': 'draft',
                    'created_date': datetime.now().strftime("%Y-%m-%d"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(self.agent.csv_path, index=False)
                
                messagebox.showinfo("Success", f"Campaign added: {campaign_id}")
                dialog.destroy()
                self.load_campaigns()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add campaign: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_campaign).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def process_text(self):
        """Process selected campaign text"""
        selection = self.campaign_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            text = campaign.get('presentation_text', '')
            if pd.isna(text) or not text:
                messagebox.showwarning("Warning", "No text to process")
                return
            
            # Simple text cleaning
            cleaned = ' '.join(text.split())  # Remove extra whitespace
            if cleaned and not cleaned.endswith('.'):
                cleaned += '.'
            
            # Update CSV
            df.loc[df['campaign_id'] == campaign_id, 'clean_text'] = cleaned
            df.to_csv(self.agent.csv_path, index=False)
            
            messagebox.showinfo("Success", "Text cleaned and saved")
            self.load_campaigns()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process text: {e}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("="*60)
    print("DeskAgent v1 - Complete Fundraising System")
    print("="*60)
    print(f"Data directory: {BASE_DIR / 'data'}")
    print(f"CSV file: {BASE_DIR / 'data' / '.csv' / 'campaigns_master.csv'}")
    print(f"Chrome profile: {BASE_DIR / 'data' / 'chrome_profile'}")
    print("="*60)
    
    app = DeskAgentGUI()
    app.run()