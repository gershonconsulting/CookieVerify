#!/usr/bin/env python3
"""
CookieVerify.com - Simple Deployment Startup Script
Pure Python - No Cloudflare, No Wrangler, No Node.js
"""

import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting CookieVerify.com Services...\n")
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    if result.returncode != 0:
        print("❌ Failed to install dependencies")
        sys.exit(1)
    print("✅ Dependencies installed\n")
    
    # Start API server
    print("🔧 Starting API Server (port 5061)...")
    api_process = subprocess.Popen([sys.executable, "proxy_server.py"])
    
    # Start web server
    print("🌐 Starting Web Server (port 5060)...")
    web_process = subprocess.Popen([
        sys.executable, "-m", "http.server", "5060",
        "--bind", "0.0.0.0",
        "--directory", "build/web"
    ])
    
    print("\n✅ CookieVerify.com is running!")
    print("📍 Web App: http://localhost:5060")
    print("📍 API: http://localhost:5061\n")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping services...")
        api_process.terminate()
        web_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
