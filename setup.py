#!/usr/bin/env python3
"""
Setup script for Restaurant Review Dashboard
Creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os

def create_virtual_environment():
    """Create Python virtual environment"""
    try:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("Installing dependencies...")
        
        # Determine the correct pip path based on OS
        if os.name == 'nt':  # Windows
            pip_path = os.path.join("venv", "Scripts", "pip")
        else:  # Unix/Linux/macOS
            pip_path = os.path.join("venv", "bin", "pip")
        
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up Restaurant Review Dashboard...")
    
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    print("\n✓ Setup completed successfully!")
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. Activate virtual environment: venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Run the Flask app: python app.py")
    print("3. Open browser to: http://localhost:8000")

if __name__ == "__main__":
    main()