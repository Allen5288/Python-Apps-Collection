#!/usr/bin/env python3
"""
FastAPI Project Initialization Script
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"→ {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr.strip()}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Please activate the virtual environment:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("   source venv/bin/activate")
        return False
    
    print("✅ Virtual environment is active")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    return run_command("pip install -r requirements.txt", "Installing Python packages")


def setup_environment_file():
    """Create .env file from example"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from template...")
            run_command("cp .env.example .env", "Copying environment file")
            print("⚠️  Please update the .env file with your configuration")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file exists")


def initialize_database():
    """Initialize database with Alembic"""
    print("Initializing database...")
    
    # Check if alembic is configured
    if not os.path.exists("alembic"):
        print("Setting up Alembic...")
        if not run_command("alembic init alembic", "Initializing Alembic"):
            return False
    
    # Create initial migration
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        print("⚠️  Migration may already exist")
    
    # Apply migrations
    return run_command("alembic upgrade head", "Applying database migrations")


def run_tests():
    """Run the test suite"""
    print("Running tests...")
    return run_command("pytest tests/ -v", "Running test suite")


def main():
    """Main setup function"""
    print("🚀 FastAPI Project Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("Please activate virtual environment and run this script again")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment file
    setup_environment_file()
    
    # Initialize database
    if not initialize_database():
        print("⚠️  Database initialization may have failed")
    
    # Run tests
    if run_tests():
        print("✅ All tests passed")
    else:
        print("⚠️  Some tests failed")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Run: uvicorn app.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
