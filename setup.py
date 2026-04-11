#!/usr/bin/env python3
"""
HorseClaw Setup Script
Quick setup for new installations
"""

import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install required packages."""
    print("\n📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    print("✅ Dependencies installed")


def create_env_file():
    """Create environment file template."""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env already exists, skipping")
        return
    
    print("\n📝 Creating .env file...")
    env_content = """# HorseClaw Environment Configuration
# Copy this file to .env and fill in your values

# Optional: Custom state file location
# STATE_FILE=horseclaw_state.json

# Optional: Default language (en or zh)
# LANGUAGE=en
"""
    env_file.write_text(env_content)
    print("✅ .env file created")


def run_tests():
    """Run test suite."""
    print("\n🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
        print("✅ All tests passed")
    except subprocess.CalledProcessError:
        print("⚠️  Some tests failed (non-critical for setup)")


def main():
    """Main setup function."""
    print("🐴 HorseClaw Setup")
    print("=" * 50)
    
    check_python_version()
    install_dependencies()
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("  1. Edit .env file with your preferences")
    print("  2. Run: python examples/usage_demo.py")
    print("  3. Or import: from horseclaw import HorseClaw")
    print("\n📖 Documentation: README.md")
    print("🐛 Issues: https://github.com/TektonXYZ/horseclaw/issues")


if __name__ == "__main__":
    main()
