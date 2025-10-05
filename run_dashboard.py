#!/usr/bin/env python3
"""
WhatsApp Support Analytics Dashboard Launcher
Run this script to start the Streamlit dashboard
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'numpy',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with:")
        print("   pip install -r requirements_dashboard.txt")
        return False
    
    return True

def check_data_file():
    """Check if the Excel data file exists"""
    if not os.path.exists('support_analysis.xlsx'):
        print("❌ Data file 'support_analysis.xlsx' not found!")
        print("💡 Please run extract.py first to generate the analysis data.")
        return False
    return True

def main():
    """Main launcher function"""
    print("🚀 Starting WhatsApp Support Analytics Dashboard...")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check data file
    if not check_data_file():
        sys.exit(1)
    
    print("✅ All requirements met!")
    print("🌐 Starting dashboard...")
    print("=" * 60)
    
    # Launch Streamlit dashboard
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'dashboard.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
