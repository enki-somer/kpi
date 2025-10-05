#!/usr/bin/env python3
"""
Quick Streamlit Dashboard Deployment Helper
This script helps you deploy your dashboard to Streamlit Community Cloud
"""

import os
import subprocess
import webbrowser
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    required_files = [
        'dashboard.py',
        'support_analysis.xlsx', 
        'requirements_dashboard.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found!")
    return True

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/

# Data files (optional - remove if you want to include Excel files)
*.xlsx
*.csv

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def create_readme():
    """Create README.md for GitHub"""
    readme_content = """# WhatsApp Support Analytics Dashboard

A beautiful Streamlit dashboard for analyzing WhatsApp support chat data.

## Features

- 📊 Interactive KPIs and metrics
- 📈 Response time analysis
- 👥 Support staff performance tracking
- 🎯 Issue categorization and trends
- 📋 Detailed data tables

## Data

This dashboard analyzes WhatsApp support chat data and provides insights into:
- Issue resolution rates
- Response times
- Support staff performance
- Peak issue hours
- Category distribution

## Usage

The dashboard automatically loads data from `support_analysis.xlsx` and provides interactive visualizations.

## Deployment

This dashboard is deployed on Streamlit Community Cloud for easy sharing and access.
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✅ Created README.md file")

def show_deployment_steps():
    """Show step-by-step deployment instructions"""
    print("\n" + "="*60)
    print("🚀 STREAMLIT COMMUNITY CLOUD DEPLOYMENT")
    print("="*60)
    
    print("\n📋 STEP-BY-STEP INSTRUCTIONS:")
    print("\n1️⃣  Create GitHub Repository:")
    print("   • Go to https://github.com")
    print("   • Click 'New repository'")
    print("   • Name it 'whatsapp-dashboard' (or any name)")
    print("   • Make it PUBLIC (important!)")
    print("   • Don't initialize with README (we'll add files)")
    
    print("\n2️⃣  Upload Files to GitHub:")
    print("   • Upload these files to your repository:")
    print("     - dashboard.py")
    print("     - support_analysis.xlsx") 
    print("     - requirements_dashboard.txt")
    print("     - README.md (created)")
    print("     - .gitignore (created)")
    
    print("\n3️⃣  Deploy to Streamlit Cloud:")
    print("   • Go to https://share.streamlit.io")
    print("   • Click 'New app'")
    print("   • Connect your GitHub account")
    print("   • Select your repository")
    print("   • Main file: dashboard.py")
    print("   • Click 'Deploy'")
    
    print("\n4️⃣  Share with Friend:")
    print("   • You'll get a URL like: https://yourusername-whatsapp-dashboard.streamlit.app")
    print("   • Share this URL with your friend!")
    
    print("\n⏱️  Total time: ~5 minutes")
    print("💰 Cost: FREE")

def open_github():
    """Open GitHub in browser"""
    try:
        webbrowser.open('https://github.com/new')
        print("🌐 Opening GitHub in your browser...")
    except:
        print("Please manually go to: https://github.com/new")

def open_streamlit():
    """Open Streamlit Cloud in browser"""
    try:
        webbrowser.open('https://share.streamlit.io')
        print("🌐 Opening Streamlit Cloud in your browser...")
    except:
        print("Please manually go to: https://share.streamlit.io")

def main():
    """Main deployment helper"""
    print("🚀 WhatsApp Dashboard Deployment Helper")
    print("="*50)
    
    # Check files
    if not check_files():
        print("\n❌ Please ensure all required files exist before deploying.")
        return
    
    # Create helper files
    create_gitignore()
    create_readme()
    
    # Show instructions
    show_deployment_steps()
    
    # Ask user what they want to do
    print("\n" + "="*60)
    print("🎯 WHAT WOULD YOU LIKE TO DO?")
    print("="*60)
    print("1. Open GitHub to create repository")
    print("2. Open Streamlit Cloud to deploy")
    print("3. Show instructions again")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            open_github()
            break
        elif choice == '2':
            open_streamlit()
            break
        elif choice == '3':
            show_deployment_steps()
        elif choice == '4':
            print("👋 Good luck with your deployment!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
