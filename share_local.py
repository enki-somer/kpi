#!/usr/bin/env python3
"""
Quick Local Sharing Script
Share your dashboard on local network instantly
"""

import subprocess
import socket
import platform
import webbrowser
import time

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def run_dashboard():
    """Run dashboard on local network"""
    local_ip = get_local_ip()
    port = 8501
    
    print("🚀 Starting WhatsApp Dashboard...")
    print(f"📡 Local IP: {local_ip}")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: http://{local_ip}:{port}")
    print("\n" + "="*50)
    print("📱 SHARE THIS URL WITH YOUR FRIEND:")
    print(f"   http://{local_ip}:{port}")
    print("="*50)
    print("\n⚠️  Make sure you're on the same WiFi network!")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print("\n" + "="*50)
    
    try:
        # Run streamlit
        subprocess.run([
            'streamlit', 'run', 'dashboard.py',
            '--server.address', '0.0.0.0',
            '--server.port', str(port),
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using it!")

if __name__ == "__main__":
    run_dashboard()
