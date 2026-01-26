import pandas as pd
import json
import os
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv

class DeskAgentV1:
    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"
        self.csv_path = self.desktop_path / "campaigns_master.csv"
        self.notes_path = self.desktop_path / "agent_notes.txt"
        self.config_path = self.desktop_path / "config.txt"
        self.initialize_files()
        
    def initialize_files(self):
        # Initialize CSV structure if not exists
        if not self.csv_path.exists():
            df = pd.DataFrame(columns=[
                'campaign_id', 'name', 'email', 'phone', 'title', 
                'presentation_text', 'clean_text', 'suggested_title',
                'whatsapp_message', 'whydonate_url', 'status',
                'created_date', 'last_updated', 'category', 'target_amount',
                'campaign_image', 'tags', 'donation_type'
            ])
            df.to_csv(self.csv_path, index=False)
            
        # Initialize notes file
        if not self.notes_path.exists():
            with open(self.notes_path, 'w') as f:
                f.write("=== DeskAgent v1 Notes ===\n")
                f.write(f"Initialized: {datetime.now()}\n\n")
                
        # Initialize config file
        if not self.config_path.exists():
            config = {
                "whydonate": {
                    "username": "",
                    "password": "",
                    "api_key": "",
                    "auto_login": False
                },
                "whatsapp": {
                    "webhook_url": "",
                    "api_token": ""
                },
                "desktop": {
                    "auto_start": True,
                    "check_interval": 300
                }
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
    
    def clean_and_improve_text(self, text):
        """Clean and improve campaign presentation text"""
        if not text or pd.isna(text):
            return ""
            
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Capitalize first letter of each sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.capitalize() for s in sentences if s.strip()]
        text = ' '.join(sentences)
        
        # Ensure proper punctuation
        if not text.endswith(('.', '!', '?')):
            text += '.'
            
        # Add formatting suggestions
        improvements = [
            "Consider adding:",
            "✓ Clear goal statement",
            "✓ Personal story connection",
            "✓ Specific use of funds",
            "✓ Regular updates planned"
        ]
        
        return text + "\n\n" + "\n".join(improvements)
    
    def suggest_campaign_title(self, name, presentation_text):
        """Generate campaign title suggestions"""
        import random
        
        # Extract key phrases from text
        words = presentation_text.lower().split()
        key_words = [w for w in words if len(w) > 4][:5]
        
        templates = [
            f"Support {name}'s Journey",
            f"Help {name} Make a Difference",
            f"{name}'s Fundraising Campaign",
            f"Join {name}'s Cause",
            f"Together for {name}"
        ]
        
        if key_words:
            templates.append(f"{name}'s {' '.join(key_words[:2])} Campaign")
            
        return random.choice(templates)
    
    def draft_whatsapp_message(self, name, title, url):
        """Draft WhatsApp message with campaign link"""
        templates = [
            f"🌟 *{title}*\n\nHi! I'm raising funds for an important cause. "
            f"Would you consider supporting us? Every contribution helps!\n\n"
            f"Campaign Link: {url}\n\n"
            f"Thank you for your generosity!\n- {name}",
            
            f"🙏 *Join Our Cause*\n\n"
            f"Hello! {name} here. I've started a fundraising campaign: '{title}'.\n\n"
            f"Your support would mean the world to us. Please check out our campaign:\n"
            f"{url}\n\n"
            f"Share with friends who might be interested too!",
            
            f"📢 *Fundraising Campaign Alert*\n\n"
            f"Dear friends, I'm excited to share my new campaign: {title}\n\n"
            f"Your donation can make a real difference. Click here to learn more:\n"
            f"{url}\n\n"
            f"With gratitude,\n{name}"
        ]
        
        import random
        return random.choice(templates)
    
    def process_campaigns(self):
        """Process all campaigns in CSV"""
        try:
            df = pd.read_csv(self.csv_path)
            
            for idx, row in df.iterrows():
                if pd.isna(row.get('clean_text')) and not pd.isna(row.get('presentation_text')):
                    # Clean text
                    df.at[idx, 'clean_text'] = self.clean_and_improve_text(row['presentation_text'])
                    
                    # Suggest title
                    if pd.isna(row.get('suggested_title')):
                        df.at[idx, 'suggested_title'] = self.suggest_campaign_title(
                            row.get('name', 'Campaign'),
                            row.get('presentation_text', '')
                        )
                    
                    # Draft WhatsApp message if URL exists
                    if not pd.isna(row.get('whydonate_url')):
                        df.at[idx, 'whatsapp_message'] = self.draft_whatsapp_message(
                            row.get('name', ''),
                            row.get('suggested_title', row.get('title', '')),
                            row.get('whydonate_url')
                        )
                    
                    df.at[idx, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            self.log_error(f"Error processing campaigns: {e}")
            return False
    
    def add_note(self, note):
        """Add note to agent_notes.txt"""
        with open(self.notes_path, 'a') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"{note}\n")
            f.write("-" * 40 + "\n")
    
    def log_error(self, error_msg):
        """Log error to notes"""
        self.add_note(f"ERROR: {error_msg}")
    
    def create_form_data(self, campaign_data):
        """Create formatted data for Whydonate form"""
        form_template = {
            "campaign_details": {
                "title": campaign_data.get('suggested_title', campaign_data.get('title', '')),
                "description": campaign_data.get('clean_text', campaign_data.get('presentation_text', '')),
                "category": campaign_data.get('category', 'General'),
                "target_amount": float(campaign_data.get('target_amount', 1000)),
                "currency": "EUR"
            },
            "organizer_details": {
                "name": campaign_data.get('name', ''),
                "email": campaign_data.get('email', ''),
                "phone": campaign_data.get('phone', ''),
                "country": "Netherlands"
            },
            "campaign_settings": {
                "donation_type": campaign_data.get('donation_type', 'one-time'),
                "allow_anonymous": True,
                "enable_updates": True,
                "tags": campaign_data.get('tags', '').split(',') if campaign_data.get('tags') else []
            },
            "media": {
                "main_image": campaign_data.get('campaign_image', ''),
                "gallery_images": []
            }
        }
        return form_template


class DeskAgentGUI:
    def __init__(self):
        self.agent = DeskAgentV1()
        self.root = tk.Tk()
        self.root.title("DeskAgent v1 - Fundraising Campaign Manager")
        self.root.geometry("900x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(label="Save CSV", command=self.save_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Campaign List
        ttk.Label(main_frame, text="Campaigns", font=('Arial', 14)).grid(row=0, column=0, sticky=tk.W)
        
        self.campaign_tree = ttk.Treeview(main_frame, columns=('ID', 'Name', 'Title', 'Status'), show='headings', height=10)
        self.campaign_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        for col in ('ID', 'Name', 'Title', 'Status'):
            self.campaign_tree.heading(col, text=col)
            self.campaign_tree.column(col, width=150)
        
        # Campaign Details
        details_frame = ttk.LabelFrame(main_frame, text="Campaign Details", padding="10")
        details_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Form fields
        fields = ['name', 'email', 'phone', 'title', 'category', 'target_amount']
        self.entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(details_frame, text=field.replace('_', ' ').title()).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(details_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[field] = entry
        
        # Presentation Text
        ttk.Label(details_frame, text="Presentation Text").grid(row=len(fields), column=0, sticky=tk.W)
        self.presentation_text = scrolledtext.ScrolledText(details_frame, width=50, height=6)
        self.presentation_text.grid(row=len(fields), column=1, padx=5, pady=5)
        
        # Cleaned Text
        ttk.Label(details_frame, text="Cleaned Text").grid(row=len(fields)+1, column=0, sticky=tk.W)
        self.cleaned_text = scrolledtext.ScrolledText(details_frame, width=50, height=6, state='disabled')
        self.cleaned_text.grid(row=len(fields)+1, column=1, padx=5, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Process Campaign", command=self.process_campaign).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate WhatsApp", command=self.generate_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Form Data", command=self.create_form_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh List", command=self.load_campaigns).pack(side=tk.LEFT, padx=5)
        
        # WhatsApp Message Display
        ttk.Label(main_frame, text="WhatsApp Message", font=('Arial', 12)).grid(row=4, column=0, sticky=tk.W, pady=(10,0))
        self.whatsapp_display = scrolledtext.ScrolledText(main_frame, width=80, height=8)
        self.whatsapp_display.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.load_campaigns()
    
    def load_campaigns(self):
        """Load campaigns into treeview"""
        for item in self.campaign_tree.get_children():
            self.campaign_tree.delete(item)
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            for _, row in df.iterrows():
                self.campaign_tree.insert('', 'end', values=(
                    row.get('campaign_id', ''),
                    row.get('name', ''),
                    row.get('title', ''),
                    row.get('status', '')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load campaigns: {e}")
    
    def process_campaign(self):
        """Process selected campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a campaign")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = pd.read_csv(self.agent.csv_path)
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            # Update text areas
            self.presentation_text.delete(1.0, tk.END)
            self.presentation_text.insert(1.0, campaign.get('presentation_text', ''))
            
            # Clean text
            cleaned = self.agent.clean_and_improve_text(campaign.get('presentation_text', ''))
            self.cleaned_text.config(state='normal')
            self.cleaned_text.delete(1.0, tk.END)
            self.cleaned_text.insert(1.0, cleaned)
            self.cleaned_text.config(state='disabled')
            
            # Update fields
            for field in self.entries:
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, str(campaign.get(field, '')))
            
            self.status_var.set(f"Processed campaign: {campaign_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process campaign: {e}")
    
    def generate_whatsapp(self):
        """Generate WhatsApp message"""
        try:
            name = self.entries['name'].get()
            title = self.entries['title'].get()
            
            if not name or not title:
                messagebox.showwarning("Warning", "Name and title are required")
                return
            
            # Simulate URL (in real scenario, this would come from Whydonate)
            url = f"https://whydonate.com/campaign/{title.lower().replace(' ', '-')}"
            
            message = self.agent.draft_whatsapp_message(name, title, url)
            self.whatsapp_display.delete(1.0, tk.END)
            self.whatsapp_display.insert(1.0, message)
            
            self.status_var.set("WhatsApp message generated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate message: {e}")
    
    def create_form_data(self):
        """Create form data for Whydonate"""
        try:
            campaign_data = {field: self.entries[field].get() for field in self.entries}
            campaign_data['presentation_text'] = self.presentation_text.get(1.0, tk.END).strip()
            
            form_data = self.agent.create_form_data(campaign_data)
            
            # Save form data
            form_path = self.agent.desktop_path / f"form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(form_path, 'w') as f:
                json.dump(form_data, f, indent=2)
            
            self.status_var.set(f"Form data saved to: {form_path.name}")
            messagebox.showinfo("Success", f"Form data saved to:\n{form_path.name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create form data: {e}")
    
    def load_csv(self):
        """Load CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_csv(file_path)
                df.to_csv(self.agent.csv_path, index=False)
                self.load_campaigns()
                self.status_var.set(f"Loaded CSV: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")
    
    def save_csv(self):
        """Save CSV file"""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_csv(self.agent.csv_path)
                df.to_csv(file_path, index=False)
                self.status_var.set(f"Saved CSV: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV: {e}")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DeskAgentGUI()
    app.run()