# DeskAgent v1

Automated fundraising campaign manager for Whydonate.

## Quick Start

A. **Install requirements:**

		pip install -r requirements.txt

B. **Run DeskAgent v1:**

1. Setup Chrome profile (one time):
   		· Run: python scripts/profile_setup.py
   		· Manually login to Whydonate with VPN
   		· Close browser
		
2. Run DeskAgent:
```
	python scripts/deskagent_v1.py
```
	
C.	**Features**

	· Campaign Management: Add/edit campaigns in CSV
	· Text Processing: Clean and improve campaign text
	· Whydonate Automation: Create campaigns automatically
	· WhatsApp Messages: Generate sharing messages
	· Persistent Sessions: Login once, use forever

File Structure

```DeskAgent-v1-Desktop-Application/
├── data/
│   ├── .csv/campaigns_master.csv     # Campaign database
│   └── chrome_profile/               # Chrome session data
├── scripts/
│   ├── deskagent_v1.py              # Main application
│   └── requirements.txt             # Python dependencies
└── README.md
```

Notes

	· Requires VPN connection to Netherlands for Whydonate access
	· ChromeDriver must match your Chrome version
	· First login must be done manually due to Whydonate's bug

	NO PUN INTENDED.
