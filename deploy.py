#!/usr/bin/env python3
"""
Quick deployment script for Restaurant Review Dashboard
"""

import os
import sys
import subprocess
import json

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check if git is available
    if not run_command("git --version", "Checking Git"):
        print("❌ Git is required for deployment")
        return False
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("⚠️  Not in a git repository. Initializing...")
        run_command("git init", "Initializing Git repository")
        run_command("git add .", "Adding files to Git")
        run_command('git commit -m "Initial commit"', "Creating initial commit")
    
    return True

def deploy_railway():
    """Deploy to Railway"""
    print("\n🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    if not run_command("railway --version", "Checking Railway CLI"):
        print("📦 Installing Railway CLI...")
        if not run_command("npm install -g @railway/cli", "Installing Railway CLI"):
            print("❌ Failed to install Railway CLI. Please install Node.js first.")
            return False
    
    # Login to Railway
    print("🔐 Please login to Railway in your browser...")
    if not run_command("railway login", "Logging into Railway"):
        return False
    
    # Link or create project
    if not run_command("railway link", "Linking Railway project"):
        return False
    
    # Deploy
    if run_command("railway up", "Deploying to Railway"):
        print("🎉 Railway deployment successful!")
        print("📝 Don't forget to set environment variables in Railway dashboard:")
        print("   - SERPAPI_KEY: 21fb6a53e8611b38fa10664a012d46729f86e7a31bdd6b54e15b99fa89ca0bc5")
        print("   - PLACE_ID: central-park-boathouse-new-york-2")
        return True
    
    return False

def deploy_vercel():
    """Deploy to Vercel"""
    print("\n▲ Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("📦 Installing Vercel CLI...")
        if not run_command("npm install -g vercel", "Installing Vercel CLI"):
            print("❌ Failed to install Vercel CLI. Please install Node.js first.")
            return False
    
    # Login to Vercel
    print("🔐 Please login to Vercel in your browser...")
    if not run_command("vercel login", "Logging into Vercel"):
        return False
    
    # Deploy
    if run_command("vercel --prod", "Deploying to Vercel"):
        print("🎉 Vercel deployment successful!")
        print("📝 Environment variables are already configured in vercel.json")
        return True
    
    return False

def main():
    """Main deployment function"""
    print("🚀 Restaurant Review Dashboard Deployment Script")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    print("\nChoose deployment platform:")
    print("1. Railway (Recommended)")
    print("2. Vercel")
    print("3. Both")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    success = False
    
    if choice == "1":
        success = deploy_railway()
    elif choice == "2":
        success = deploy_vercel()
    elif choice == "3":
        railway_success = deploy_railway()
        vercel_success = deploy_vercel()
        success = railway_success or vercel_success
    elif choice == "4":
        print("👋 Deployment cancelled")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Check your deployment dashboard for the live URL")
        print("2. Verify environment variables are set correctly")
        print("3. Test the application using the /health endpoint")
        print("4. Monitor logs for any issues")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()