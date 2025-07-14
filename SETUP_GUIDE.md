# ICT Scanner Setup Guide

## Step 1: Install Git
1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart your computer

## Step 2: Set Up Git Identity
Open Git Bash and run:
```bash
git config --global user.name "Markus Goroshin"
git config --global user.email "markusgoroshin@gmail.com"
```

## Step 3: Create GitHub Repository
1. Go to github.com and sign in
2. Click the "+" button → "New repository"
3. Name it: `ict-scanner`
4. Add description: "ICT Price Delivery Array Scanner for MES/MNQ Futures"
5. Choose "Public" or "Private"
6. Check "Add a README file"
7. Click "Create repository"

## Step 4: Set Up Local Repository
1. Open Git Bash
2. Navigate to your project folder:
   ```bash
   cd "C:\Users\marku\ict-scanner"
   ```
3. Run the setup script:
   ```bash
   ./setup_git.bat
   ```
   Or manually:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: ICT PD Array Scanner"
   ```

## Step 5: Connect to GitHub
Replace `YOUR_USERNAME` with your GitHub username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/ict-scanner.git
git push -u origin main
```

## Step 6: Install Python Dependencies
1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 7: Configure the Scanner
1. Copy the template config:
   ```bash
   copy config.template.yaml config.yaml
   ```
2. Edit `config.yaml` with your settings

## Project Structure
```
ict-scanner/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── main_scanner.py       # Main entry point
├── config.template.yaml  # Configuration template
├── .gitignore           # Git ignore rules
├── setup_git.bat        # Git setup script
├── SETUP_GUIDE.md       # This file
└── src/                 # Source code
    ├── config.py        # Configuration management
    ├── data_sources/    # Market data sources
    ├── patterns/        # Pattern detection
    ├── alerts/          # Alert system
    └── utils/           # Utilities
```

## Next Steps
1. Complete the source code files in the `src/` directory
2. Set up your data source credentials
3. Configure alert channels (Discord, Telegram, etc.)
4. Test the scanner with paper trading

## Troubleshooting
- If Git commands fail, make sure Git is installed and in your PATH
- If Python commands fail, make sure Python 3.9+ is installed
- Check the logs in the `logs/` directory for errors 