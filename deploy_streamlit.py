#!/usr/bin/env python3
"""
Deployment script for MORVO Streamlit application
"""

import os
import subprocess
import sys
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the application.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    try:
        print("🚀 Starting Streamlit application...")
        print("📱 The application will be available at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

def build_docker():
    """Build Docker image for Streamlit"""
    try:
        print("🐳 Building Docker image...")
        subprocess.run([
            "docker", "build", 
            "-f", "Dockerfile.streamlit",
            "-t", "morvo-streamlit:latest",
            "."
        ], check=True)
        print("✅ Docker image built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Docker image: {e}")
        return False

def run_docker():
    """Run the application in Docker"""
    try:
        print("🐳 Starting Docker container...")
        print("📱 The application will be available at: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the container")
        
        subprocess.run([
            "docker", "run", 
            "-p", "8501:8501",
            "--env-file", ".env",
            "morvo-streamlit:latest"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Container stopped by user")
    except Exception as e:
        print(f"❌ Failed to run Docker container: {e}")

def main():
    """Main deployment function"""
    print("🤖 MORVO Streamlit Deployment Script")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python deploy_streamlit.py local     # Run locally")
        print("  python deploy_streamlit.py docker    # Run in Docker")
        print("  python deploy_streamlit.py build     # Build Docker image only")
        return
    
    command = sys.argv[1].lower()
    
    if not check_environment():
        return
    
    if command == "local":
        if install_dependencies():
            run_streamlit()
    elif command == "docker":
        if build_docker():
            run_docker()
    elif command == "build":
        build_docker()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: local, docker, build")

if __name__ == "__main__":
    main() 