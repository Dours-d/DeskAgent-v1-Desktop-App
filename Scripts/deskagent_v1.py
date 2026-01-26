import pandas as pd
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv
import hashlib

# Get the base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

class DeskAgentV1:
    def __init__(self):
        # Define paths
        self.base_dir = BASE_DIR
        self.data_dir = self.base_dir / "data"
        self.csv_dir = self.data_dir / ".csv"  # Special .csv directory
        self.scripts_dir = self.base_dir / "scripts"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.csv_path = self.csv_dir / "campaigns_master.csv"  # Correct path!
        self.notes_path = self.data_dir / "agent_notes.txt"
        self.config_path = self.data_dir / "config.txt"
        self.exports_dir = self.data_dir / "exports"
        self.backup_dir = self.data_dir / "backups"
        
        # Create subdirectories
        self.exports_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.initialize_files()
        
    def initialize_files(self):
        """Initialize all required files with proper structure"""
        try:
            # Initialize CSV structure if not exists
            if not self.csv_path.exists():
                self.create_empty_csv()
                self.log_event("Created campaigns_master.csv in data/.csv/")
            else:
                # Validate existing CSV
                self.validate_csv_structure()
                
            # Initialize notes file
            if not self.notes_path.exists():
                self.create_notes_file()
                
            # Initialize config file
            if not self.config_path.exists():
                self.create_config_file()
                
        except Exception as e:
            self.log_error(f"Initialization failed: {str(e)}")
            raise
    
    def create_empty_csv(self):
        """Create empty CSV with correct structure"""
        columns = [
            'campaign_id', 'name', 'email', 'phone', 'title', 
            'presentation_text', 'clean_text', 'suggested_title',
            'whatsapp_message', 'whydonate_url', 'status',
            'created_date', 'last_updated', 'category', 'target_amount',
            'campaign_image', 'tags', 'donation_type', 'notes',
            'whatsapp_sent', 'email_sent', 'last_contacted'
        ]
        
        df = pd.DataFrame(columns=columns)
        df.to_csv(self.csv_path, index=False, encoding='utf-8')
    
    def validate_csv_structure(self):
        """Validate and fix CSV structure if needed"""
        try:
            df = pd.read_csv(self.csv_path)
            required_columns = ['campaign_id', 'name', 'email', 'phone', 'title']
            
            # Check for missing columns
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                self.log_event(f"CSV missing columns: {missing_cols}. Fixing...")
                for col in missing_cols:
                    df[col] = ""
                df.to_csv(self.csv_path, index=False)
                self.log_event("CSV structure fixed")
                
        except Exception as e:
            self.log_event(f"CSV validation error: {e}. Creating new CSV.")
            self.create_empty_csv()
    
    def create_notes_file(self):
        """Create agent notes file"""
        with open(self.notes_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("DESKAGENT v1 - AGENT NOTES\n")
            f.write("=" * 70 + "\n")
            f.write(f"Initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Directory: {self.data_dir}\n")
            f.write(f"CSV Location: {self.csv_path}\n")
            f.write("-" * 70 + "\n\n")
    
    def create_config_file(self):
        """Create configuration file"""
        config = {
            "system": {
                "version": "1.0.0",
                "data_path": str(self.data_dir),
                "csv_path": str(self.csv_path),
                "backup_enabled": True,
                "auto_backup_count": 5
            },
            "paths": {
                "data_directory": str(self.data_dir),
                "csv_directory": str(self.csv_dir),
                "scripts_directory": str(self.scripts_dir),
                "exports_directory": str(self.exports_dir),
                "backup_directory": str(self.backup_dir)
            },
            "whydonate": {
                "enabled": False,
                "username": "",
                "password": "",
                "auto_login": False,
                "default_category": "General",
                "default_currency": "EUR",
                "timeout": 30
            },
            "whatsapp": {
                "enable_templates": True,
                "default_template": "standard",
                "include_link": True,
                "include_hashtags": True
            },
            "processing": {
                "auto_clean_text": True,
                "auto_suggest_title": True,
                "auto_generate_whatsapp": True,
                "backup_before_process": True,
                "create_backups": True
            },
            "ui": {
                "theme": "light",
                "font_size": 10,
                "auto_refresh": True,
                "refresh_interval": 30
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.create_config_file()
    
    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def clean_and_improve_text(self, text):
        """Clean and improve campaign presentation text"""
        if not text or pd.isna(text) or str(text).strip() == '':
            return ""
            
        text = str(text).strip()
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Capitalize first letter of each sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Ensure first letter is capitalized
                if sentence and sentence[0].islower():
                    sentence = sentence[0].upper() + sentence[1:]
                cleaned_sentences.append(sentence)
        
        text = ' '.join(cleaned_sentences)
        
        # Ensure proper punctuation
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Add formatting suggestions
        improvements = [
            "\n\n--- CAMPAIGN IMPROVEMENT SUGGESTIONS ---",
            "✓ Add a clear goal statement",
            "✓ Include personal story/connection",
            "✓ Specify how funds will be used",
            "✓ Mention who will benefit",
            "✓ Plan for regular updates",
            "✓ Include a call-to-action"
        ]
        
        return text + "\n" + "\n".join(improvements)
    
    def suggest_campaign_title(self, name, presentation_text, category=""):
        """Generate campaign title suggestions"""
        import random
        
        name = str(name).strip() if name else "Campaign"
        
        # Extract keywords from text
        words = str(presentation_text).lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in ['about', 'their', 'would', 'could']][:3]
        
        templates = [
            f"Support {name}'s Journey",
            f"Help {name} Make a Difference",
            f"{name}'s Fundraising Campaign",
            f"Join {name}'s Cause",
            f"Together for {name}",
            f"{name}'s Mission",
            f"Empowering {name}"
        ]
        
        # Category-based titles
        if category:
            category_titles = [
                f"{name}'s {category} Fund",
                f"{category} Support for {name}",
                f"Help {name} with {category}"
            ]
            templates.extend(category_titles)
        
        # Keyword-based titles
        if keywords:
            kw_title = f"{name}'s {', '.join(keywords[:2])} Campaign"
            templates.append(kw_title)
        
        # Select 3 random suggestions
        selected = random.sample(templates, min(3, len(templates)))
        return selected
    
    def draft_whatsapp_message(self, name, title, url, template="standard"):
        """Draft WhatsApp message with campaign link"""
        templates = {
            "standard": f"""🌟 *{title}*

Hi! I'm {name} and I've started a fundraising campaign. 
Your support would mean the world to us!

📋 Campaign Details: {title}
🔗 Donate here: {url}

Every contribution helps us get closer to our goal. 
Thank you for your generosity!

Best regards,
{name}""",
            
            "urgent": f"""🚨 *URGENT: {title}*

Dear friends, 

I'm {name} and we urgently need your support for our campaign: {title}

Time is critical and your help can make a real difference.

🔗 Please donate now: {url}

Even small amounts help. Please share widely!

Thank you,
{name}""",
            
            "thank_you": f"""🙏 *Thank You for Your Support!*

Hello! This is {name}.

Thank you so much for considering our campaign: {title}

Your support means everything to us. 
If you'd like to contribute or share:

🔗 Campaign link: {url}

With heartfelt gratitude,
{name}"""
        }
        
        return templates.get(template, templates["standard"])
    
    def backup_csv(self):
        """Create a backup of the CSV file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"campaigns_master_backup_{timestamp}.csv"
            
            # Read and write with proper encoding
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            df.to_csv(backup_path, index=False, encoding='utf-8')
            
            # Clean up old backups (keep last 5)
            backups = list(self.backup_dir.glob("campaigns_master_backup_*.csv"))
            if len(backups) > 5:
                for old_backup in sorted(backups)[:-5]:
                    old_backup.unlink()
            
            self.log_event(f"CSV backup created: {backup_path.name}")
            return True
            
        except Exception as e:
            self.log_error(f"Backup failed: {e}")
            return False
    
    def process_campaigns(self):
        """Process all campaigns in CSV"""
        try:
            # Create backup before processing
            config = self.load_config()
            if config.get('processing', {}).get('backup_before_process', True):
                self.backup_csv()
            
            # Read CSV
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            processed_count = 0
            for idx, row in df.iterrows():
                campaign_id = row.get('campaign_id', f"camp_{idx:04d}")
                
                # Generate campaign ID if missing
                if pd.isna(campaign_id) or not campaign_id:
                    df.at[idx, 'campaign_id'] = f"camp_{idx:04d}"
                    campaign_id = df.at[idx, 'campaign_id']
                
                # Clean and improve text
                if pd.isna(row.get('clean_text')) and not pd.isna(row.get('presentation_text')):
                    clean_text = self.clean_and_improve_text(row['presentation_text'])
                    df.at[idx, 'clean_text'] = clean_text
                    processed_count += 1
                
                # Suggest title
                if pd.isna(row.get('suggested_title')) or not row.get('suggested_title'):
                    suggestions = self.suggest_campaign_title(
                        row.get('name', 'Campaign'),
                        row.get('presentation_text', ''),
                        row.get('category', '')
                    )
                    if suggestions:
                        df.at[idx, 'suggested_title'] = ' | '.join(suggestions)
                
                # Draft WhatsApp message if URL exists
                if not pd.isna(row.get('whydonate_url')) and pd.isna(row.get('whatsapp_message')):
                    message = self.draft_whatsapp_message(
                        row.get('name', ''),
                        row.get('suggested_title', row.get('title', 'Fundraising Campaign')),
                        row.get('whydonate_url')
                    )
                    df.at[idx, 'whatsapp_message'] = message
                
                # Update timestamp
                df.at[idx, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Set created date if missing
                if pd.isna(row.get('created_date')):
                    df.at[idx, 'created_date'] = datetime.now().strftime("%Y-%m-%d")
            
            # Save processed CSV
            df.to_csv(self.csv_path, index=False, encoding='utf-8')
            
            self.log_event(f"Processed {processed_count} campaigns")
            return True
            
        except Exception as e:
            self.log_error(f"Error processing campaigns: {e}")
            return False
    
    def add_campaign(self, campaign_data):
        """Add a new campaign to CSV"""
        try:
            # Read existing data
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Generate campaign ID
            campaign_id = f"camp_{len(df) + 1:04d}"
            
            # Prepare new row
            new_row = {
                'campaign_id': campaign_id,
                'name': campaign_data.get('name', ''),
                'email': campaign_data.get('email', ''),
                'phone': campaign_data.get('phone', ''),
                'title': campaign_data.get('title', ''),
                'presentation_text': campaign_data.get('presentation_text', ''),
                'category': campaign_data.get('category', 'General'),
                'target_amount': float(campaign_data.get('target_amount', 1000)),
                'donation_type': campaign_data.get('donation_type', 'one-time'),
                'tags': campaign_data.get('tags', ''),
                'status': 'draft',
                'created_date': datetime.now().strftime("%Y-%m-%d"),
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to DataFrame
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save CSV
            df.to_csv(self.csv_path, index=False, encoding='utf-8')
            
            self.log_event(f"Added new campaign: {campaign_id} - {new_row['name']}")
            return campaign_id
            
        except Exception as e:
            self.log_error(f"Error adding campaign: {e}")
            return None
    
    def log_event(self, message):
        """Log event to notes file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(self.notes_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            print(f"LOG: {message}")
            
        except Exception as e:
            print(f"Failed to log event: {e}")
    
    def log_error(self, error_message):
        """Log error to notes file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {error_message}\n"
        
        try:
            with open(self.notes_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass
        
        print(f"ERROR: {error_message}")
    
    def get_campaign_stats(self):
        """Get statistics about campaigns"""
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            stats = {
                'total_campaigns': len(df),
                'active': len(df[df['status'] == 'active']),
                'draft': len(df[df['status'] == 'draft']),
                'completed': len(df[df['status'] == 'completed']),
                'with_urls': len(df[df['whydonate_url'].notna()]),
                'needs_processing': len(df[df['clean_text'].isna() & df['presentation_text'].notna()])
            }
            
            return stats
            
        except Exception as e:
            self.log_error(f"Error getting stats: {e}")
            return {}
    
    def export_to_json(self, campaign_ids=None):
        """Export campaigns to JSON format"""
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            if campaign_ids:
                df = df[df['campaign_id'].isin(campaign_ids)]
            
            # Convert to dictionary
            data = df.to_dict('records')
            
            # Create export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = self.exports_dir / f"campaigns_export_{timestamp}.json"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.log_event(f"Exported {len(data)} campaigns to {export_path.name}")
            return export_path
            
        except Exception as e:
            self.log_error(f"Export failed: {e}")
            return None


class DeskAgentGUI:
    def __init__(self):
        self.agent = DeskAgentV1()
        self.root = tk.Tk()
        self.root.title("DeskAgent v1 - Fundraising Campaign Manager")
        self.root.geometry("1000x750")
        
        # Set icon (if available)
        try:
            self.root.iconbitmap(self.agent.scripts_dir / "icon.ico")
        except:
            pass
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV", command=self.open_csv)
        file_menu.add_command(label="Save CSV", command=self.save_csv)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Now", command=self.backup_now)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Process All Campaigns", command=self.process_all)
        tools_menu.add_command(label="Clean All Text", command=self.clean_all_text)
        tools_menu.add_command(label="Generate All WhatsApp", command=self.generate_all_whatsapp)
        tools_menu.add_separator()
        tools_menu.add_command(label="View Stats", command=self.show_stats)
        tools_menu.add_command(label="View Notes", command=self.view_notes)
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Campaign list
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Campaign list frame
        list_frame = ttk.LabelFrame(left_panel, text="Campaigns", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search box
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_campaigns)
        
        # Campaign treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('ID', 'Name', 'Title', 'Status', 'Category', 'Updated')
        self.campaign_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        # Configure columns
        col_widths = {'ID': 80, 'Name': 150, 'Title': 200, 'Status': 80, 'Category': 100, 'Updated': 120}
        for col in columns:
            self.campaign_tree.heading(col, text=col)
            self.campaign_tree.column(col, width=col_widths.get(col, 100))
        
        self.campaign_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.campaign_tree.yview)
        tree_scroll_x.config(command=self.campaign_tree.xview)
        
        # Bind selection event
        self.campaign_tree.bind('<<TreeviewSelect>>', self.on_campaign_select)
        
        # Right panel - Campaign details
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Basic Info Tab
        basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_tab, text="Basic Info")
        self.setup_basic_tab(basic_tab)
        
        # Story Tab
        story_tab = ttk.Frame(self.notebook)
        self.notebook.add(story_tab, text="Story")
        self.setup_story_tab(story_tab)
        
        # WhatsApp Tab
        whatsapp_tab = ttk.Frame(self.notebook)
        self.notebook.add(whatsapp_tab, text="WhatsApp")
        self.setup_whatsapp_tab(whatsapp_tab)
        
        # Status bar
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.status_bar, mode='indeterminate', length=100)
        self.progress.pack(side=tk.RIGHT, padx=5)
        
    def setup_basic_tab(self, parent):
        """Setup basic info tab"""
        # Create form fields
        fields = [
            ('campaign_id', 'Campaign ID', False),
            ('name', 'Name *', True),
            ('email', 'Email', True),
            ('phone', 'Phone', True),
            ('title', 'Title *', True),
            ('suggested_title', 'Suggested Title', False),
            ('category', 'Category', True),
            ('target_amount', 'Target Amount (€)', True),
            ('donation_type', 'Donation Type', True),
            ('status', 'Status', True),
            ('whydonate_url', 'Whydonate URL', True)
        ]
        
        self.entries = {}
        
        for i, (field, label, editable) in enumerate(fields):
            row = ttk.Frame(parent)
            row.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(row, text=label, width=20, anchor=tk.W).pack(side=tk.LEFT)
            
            if editable:
                entry = ttk.Entry(row, width=50)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entries[field] = entry
            else:
                entry = ttk.Entry(row, width=50, state='readonly')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add New", command=self.add_new_campaign).pack(side=tk.LEFT, padx=5)
        
    def setup_story_tab(self, parent):
        """Setup story tab"""
        # Original text
        ttk.Label(parent, text="Original Presentation Text:").pack(anchor=tk.W, padx=10, pady=(10,5))
        
        self.original_text = scrolledtext.ScrolledText(parent, height=8, wrap=tk.WORD)
        self.original_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Cleaned text
        ttk.Label(parent, text="Cleaned & Improved Text:").pack(anchor=tk.W, padx=10, pady=(5,5))
        
        self.cleaned_text = scrolledtext.ScrolledText(parent, height=8, wrap=tk.WORD)
        self.cleaned_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Clean Text", command=self.clean_selected_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Cleaned", command=self.copy_cleaned_text).pack(side=tk.LEFT, padx=5)
        
    def setup_whatsapp_tab(self, parent):
        """Setup WhatsApp tab"""
        # Template selection
        template_frame = ttk.Frame(parent)
        template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value="standard")
        ttk.Combobox(template_frame, textvariable=self.template_var, 
                    values=["standard", "urgent", "thank_you"], 
                    state="readonly", width=15).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(template_frame, text="Generate", command=self.generate_whatsapp).pack(side=tk.LEFT, padx=10)
        
        # Message display
        self.whatsapp_display = scrolledtext.ScrolledText(parent, height=15, wrap=tk.WORD, font=("Arial", 10))
        self.whatsapp_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Copy Message", command=self.copy_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save to Campaign", command=self.save_whatsapp).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Send Test", command=self.send_test).pack(side=tk.LEFT, padx=5)
        
    def load_data(self):
        """Load data from CSV"""
        try:
            # Clear tree
            for item in self.campaign_tree.get_children():
                self.campaign_tree.delete(item)
            
            # Load CSV
            df = pd.read_csv(self.agent.csv_path, encoding='utf-8')
            
            # Populate tree
            for _, row in df.iterrows():
                self.campaign_tree.insert('', 'end', values=(
                    row.get('campaign_id', ''),
                    row.get('name', ''),
                    row.get('title', ''),
                    row.get('status', 'draft'),
                    row.get('category', 'General'),
                    row.get('last_updated', '')
                ))
            
            self.update_status(f"Loaded {len(df)} campaigns")
            
        except Exception as e:
            self.show_error(f"Failed to load data: {e}")
    
    def on_campaign_select(self, event):
        """Handle campaign selection"""
        selection = self.campaign_tree.selection()
        if not selection:
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            # Load campaign data
            df = pd.read_csv(self.agent.csv_path, encoding='utf-8')
            campaign = df[df['campaign_id'] == campaign_id].iloc[0]
            
            # Update form fields
            for field, entry in self.entries.items():
                if field in campaign:
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, str(campaign[field]))
                    if field == 'campaign_id':
                        entry.config(state='readonly')
            
            # Update text areas
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(1.0, campaign.get('presentation_text', ''))
            
            self.cleaned_text.delete(1.0, tk.END)
            self.cleaned_text.insert(1.0, campaign.get('clean_text', ''))
            
            # Update WhatsApp message if exists
            self.whatsapp_display.delete(1.0, tk.END)
            if campaign.get('whatsapp_message'):
                self.whatsapp_display.insert(1.0, campaign['whatsapp_message'])
            
        except Exception as e:
            self.show_error(f"Error loading campaign: {e}")
    
    def process_all(self):
        """Process all campaigns"""
        self.progress.start()
        self.update_status("Processing campaigns...")
        
        try:
            success = self.agent.process_campaigns()
            if success:
                self.load_data()
                self.update_status("All campaigns processed successfully")
            else:
                self.show_error("Failed to process campaigns")
        finally:
            self.progress.stop()
    
    def clean_selected_text(self):
        """Clean text for selected campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            self.show_warning("Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            # Get original text
            original_text = self.original_text.get(1.0, tk.END).strip()
            
            if not original_text:
                self.show_warning("No text to clean")
                return
            
            # Clean text
            cleaned = self.agent.clean_and_improve_text(original_text)
            self.cleaned_text.delete(1.0, tk.END)
            self.cleaned_text.insert(1.0, cleaned)
            
            # Update CSV
            df = pd.read_csv(self.agent.csv_path, encoding='utf-8')
            idx = df[df['campaign_id'] == campaign_id].index[0]
            df.at[idx, 'clean_text'] = cleaned
            df.at[idx, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_csv(self.agent.csv_path, index=False, encoding='utf-8')
            
            self.update_status("Text cleaned and saved")
            
        except Exception as e:
            self.show_error(f"Error cleaning text: {e}")
    
    def generate_whatsapp(self):
        """Generate WhatsApp message"""
        try:
            name = self.entries['name'].get()
            title = self.entries['title'].get() or self.entries['suggested_title'].get()
            url = self.entries['whydonate_url'].get()
            
            if not name or not title:
                self.show_warning("Name and title are required")
                return
            
            # Generate message
            template = self.template_var.get()
            message = self.agent.draft_whatsapp_message(name, title, url, template)
            
            # Display message
            self.whatsapp_display.delete(1.0, tk.END)
            self.whatsapp_display.insert(1.0, message)
            
            self.update_status("WhatsApp message generated")
            
        except Exception as e:
            self.show_error(f"Error generating message: {e}")
    
    def save_changes(self):
        """Save changes to selected campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            self.show_warning("Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            # Load CSV
            df = pd.read_csv(self.agent.csv_path, encoding='utf-8')
            idx = df[df['campaign_id'] == campaign_id].index[0]
            
            # Update fields
            for field, entry in self.entries.items():
                if field != 'campaign_id':  # Don't update ID
                    df.at[idx, field] = entry.get()
            
            # Update text fields
            df.at[idx, 'presentation_text'] = self.original_text.get(1.0, tk.END).strip()
            df.at[idx, 'clean_text'] = self.cleaned_text.get(1.0, tk.END).strip()
            df.at[idx, 'whatsapp_message'] = self.whatsapp_display.get(1.0, tk.END).strip()
            
            # Update timestamp
            df.at[idx, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save CSV
            df.to_csv(self.agent.csv_path, index=False, encoding='utf-8')
            
            # Refresh tree
            self.load_data()
            
            self.update_status("Changes saved successfully")
            
        except Exception as e:
            self.show_error(f"Error saving changes: {e}")
    
    def add_new_campaign(self):
        """Add a new campaign"""
        try:
            # Create new campaign data
            campaign_data = {
                'name': self.entries['name'].get(),
                'email': self.entries['email'].get(),
                'phone': self.entries['phone'].get(),
                'title': self.entries['title'].get(),
                'presentation_text': self.original_text.get(1.0, tk.END).strip(),
                'category': self.entries['category'].get(),
                'target_amount': self.entries['target_amount'].get(),
                'donation_type': self.entries['donation_type'].get()
            }
            
            # Add campaign
            campaign_id = self.agent.add_campaign(campaign_data)
            
            if campaign_id:
                # Clear form for next entry
                self.clear_form()
                self.entries['campaign_id'].config(state='normal')
                self.entries['campaign_id'].delete(0, tk.END)
                self.entries['campaign_id'].insert(0, campaign_id)
                self.entries['campaign_id'].config(state='readonly')
                
                # Refresh list
                self.load_data()
                
                self.update_status(f"Added new campaign: {campaign_id}")
            else:
                self.show_error("Failed to add campaign")
                
        except Exception as e:
            self.show_error(f"Error adding campaign: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        for field, entry in self.entries.items():
            if field != 'campaign_id':
                entry.config(state='normal')
                entry.delete(0, tk.END)
        
        self.original_text.delete(1.0, tk.END)
        self.cleaned_text.delete(1.0, tk.END)
        self.whatsapp_display.delete(1.0, tk.END)
        
        self.update_status("Form cleared")
    
    def filter_campaigns(self, event=None):
        """Filter campaigns based on search text"""
        search_text = self.search_var.get().lower()
        
        for item in self.campaign_tree.get_children():
            values = self.campaign_tree.item(item)['values']
            # Check if search text matches any value
            match = any(search_text in str(value).lower() for value in values)
            self.campaign_tree.item(item, tags=('visible' if match else 'hidden'))
        
        # Hide non-matching items
        self.campaign_tree.tag_configure('hidden', foreground='gray')
    
    def backup_now(self):
        """Create backup"""
        self.progress.start()
        self.update_status("Creating backup...")
        
        try:
            success = self.agent.backup_csv()
            if success:
                self.update_status("Backup created successfully")
            else:
                self.show_error("Backup failed")
        finally:
            self.progress.stop()
    
    def export_json(self):
        """Export to JSON"""
        try:
            export_path = self.agent.export_to_json()
            if export_path:
                self.update_status(f"Exported to: {export_path.name}")
                messagebox.showinfo("Export Successful", 
                                  f"Campaigns exported to:\n{export_path}")
            else:
                self.show_error("Export failed")
        except Exception as e:
            self.show_error(f"Export error: {e}")
    
    def show_stats(self):
        """Show campaign statistics"""
        stats = self.agent.get_campaign_stats()
        
        stats_text = "📊 Campaign Statistics\n"
        stats_text += "=" * 30 + "\n"
        for key, value in stats.items():
            stats_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        messagebox.showinfo("Campaign Statistics", stats_text)
    
    def view_notes(self):
        """View agent notes"""
        try:
            with open(self.agent.notes_path, 'r', encoding='utf-8') as f:
                notes_content = f.read()
            
            # Create notes window
            notes_window = tk.Toplevel(self.root)
            notes_window.title("Agent Notes")
            notes_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(notes_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, notes_content)
            text_widget.config(state='disabled')
            
        except Exception as e:
            self.show_error(f"Error viewing notes: {e}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.update_status(f"Error: {message}")
    
    def show_warning(self, message):
        """Show warning message"""
        messagebox.showwarning("Warning", message)
        self.update_status(f"Warning: {message}")
    
    def copy_cleaned_text(self):
        """Copy cleaned text to clipboard"""
        text = self.cleaned_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("Cleaned text copied to clipboard")
    
    def copy_whatsapp(self):
        """Copy WhatsApp message to clipboard"""
        text = self.whatsapp_display.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("WhatsApp message copied to clipboard")
    
    def save_whatsapp(self):
        """Save WhatsApp message to campaign"""
        selection = self.campaign_tree.selection()
        if not selection:
            self.show_warning("Please select a campaign first")
            return
        
        item = self.campaign_tree.item(selection[0])
        campaign_id = item['values'][0]
        
        try:
            df = pd.read_csv(self.agent.csv_path, encoding='utf-8')
            idx = df[df['campaign_id'] == campaign_id].index[0]
            
            message = self.whatsapp_display.get(1.0, tk.END).strip()
            df.at[idx, 'whatsapp_message'] = message
            df.at[idx, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            df.to_csv(self.agent.csv_path, index=False, encoding='utf-8')
            
            self.update_status("WhatsApp message saved to campaign")
            
        except Exception as e:
            self.show_error(f"Error saving message: {e}")
    
    def send_test(self):
        """Send test message (placeholder)"""
        self.update_status("Test message feature would send via WhatsApp API")
        messagebox.showinfo("Test Message", 
                          "In production, this would send via WhatsApp Business API")
    
    def open_csv(self):
        """Open CSV file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Copy file to .csv directory
                import shutil
                shutil.copy2(file_path, self.agent.csv_path)
                self.load_data()
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.show_error(f"Error loading CSV: {e}")
    
    def save_csv(self):
        """Save CSV file dialog"""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                import shutil
                shutil.copy2(self.agent.csv_path, file_path)
                self.update_status(f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                self.show_error(f"Error saving CSV: {e}")
    
    def run(self):
        """Run the application"""
        self.update_status(f"DeskAgent v1 Ready | CSV: {self.agent.csv_path}")
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("DeskAgent v1 - Fundraising Campaign Manager")
    print("=" * 60)
    print(f"Data Directory: {BASE_DIR / 'data'}")
    print(f"CSV Location: {BASE_DIR / 'data' / '.csv' / 'campaigns_master.csv'}")
    print(f"Notes File: {BASE_DIR / 'data' / 'agent_notes.txt'}")
    print("=" * 60)
    
    app = DeskAgentGUI()
    app.run()