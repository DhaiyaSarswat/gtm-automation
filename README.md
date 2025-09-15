# GTM Automation Bot 

Automates monitoring and analysis of Reddit posts for your keywords.  
Fetches posts, analyzes relevance, intent, sentiment, logs to Google Sheets, and sends Slack alerts for important posts.
---

## Project Stucture
```commandline
gtm-automation/
├── .env
├── config_keywords.py
├── google_service_account.json
├── gtm_dashboard.png
├── keywords.txt
├── main_dashboard.py
├── README.md
├── requirement_libraries.txt
└── services_analyzer.py
```
---

## Setup & Installation

### 1. Clone the repo:
```bash
git clone https://github.com/username/gtm-automation.git
cd gtm-automation
```

### 2. Create a virtual environment:
```commandline
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies:
```commandline
pip install -r requirement_libraries.txt
```

### 4. Configure keywords and API credentials in ```config_keywords.py``` and ```.env```.
Add your Google service account JSON (```google_service_account.json```) and Slack webhook if used.

### 5. Run the Bot
```commandline
python main_dashboard.py
```
---
# Notes
- Update keywords.txt to track different topics.

- Ensure Google credentials in google_service_account.json are correct.

- Output dashboard is saved as gtm_dashboard.png.
- ---