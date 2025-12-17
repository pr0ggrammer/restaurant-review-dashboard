#!/usr/bin/env python3
"""
Quick script to update and redeploy the dashboard
"""

import subprocess
import sys

def run_command(command, description):
    """Run a shell command"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Updating Restaurant Review Dashboard")
    print("=" * 50)
    
    # Git commands to push updates
    commands = [
        ("git add .", "Adding changes to Git"),
        ('git commit -m "Fix Vercel deployment and upgrade UI with blue theme and better text visibility"', "Committing changes"),
        ("git push", "Pushing to GitHub")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n❌ Failed at: {description}")
            sys.exit(1)
    
    print("\n🎉 Updates pushed successfully!")
    print("\n📋 Next steps:")
    print("1. Vercel will automatically redeploy from GitHub")
    print("2. Check your Vercel dashboard for deployment status")
    print("3. Visit your live URL to see the updated blue theme")
    print("4. Text should now be much more visible!")

if __name__ == "__main__":
    main()