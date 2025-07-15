#!/usr/bin/env python3
"""
Complete setup script for ICT Scanner
Creates all missing files and directories
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    dirs = [
        "src/data_sources",
        "src/patterns", 
        "src/alerts",
        "src/utils",
        "logs",
        "data"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def create_init_files():
    """Create __init__.py files"""
    init_dirs = [
        "src/data_sources",
        "src/patterns",
        "src/alerts", 
        "src/utils"
    ]
    
    for dir_path in init_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Package initialization\n")
            print(f"Created: {init_file}")

def main():
    """Main setup function"""
    print("Setting up ICT Scanner project structure...")
    
    create_directories()
    create_init_files()
    
    print("\nSetup complete! Next steps:")
    print("1. Install Python from python.org")
    print("2. Create virtual environment: python -m venv venv")
    print("3. Activate: venv\\Scripts\\activate")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Configure: copy config.template.yaml config.yaml")

if __name__ == "__main__":
    main() 