#!/usr/bin/env python3
"""
SONY Credentials - PyInstaller Build Script
Creates standalone Windows executable without Python dependency
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ['flask', 'pandas', 'reportlab', 'openpyxl', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies():
    """Install missing dependencies"""
    missing = check_dependencies()
    if missing:
        print(f"\n[INSTALLING] Missing packages: {', '.join(missing)}")
        for package in missing:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def main():
    """Main build process"""
    try:
        print("\n" + "="*60)
        print("  SONY Credentials - PyInstaller Build")
        print("="*60)
        
        # Check Python version
        print(f"\n[OK] Python Version: {sys.version.split()[0]}")
        print(f"[OK] Platform: {sys.platform}")
        
        # Check if PyInstaller is installed
        if not check_pyinstaller():
            print("\n[ERROR] PyInstaller not installed")
            print("Install with: pip install PyInstaller")
            return False
        
        print("[OK] PyInstaller found")
        
        # Check and install dependencies
        print("\n[CHECKING] Dependencies...")
        missing = check_dependencies()
        if missing:
            print(f"[WARNING] Missing: {', '.join(missing)}")
            install_dependencies()
        else:
            print("[OK] All dependencies installed")
        
        # Get paths
        project_root = Path(__file__).parent
        app_py = project_root / 'app.py'
        icon_file = project_root / 'icon.ico'
        dist_dir = project_root / 'dist'
        build_dir = project_root / 'build'
        
        # Check if app.py exists
        if not app_py.exists():
            print(f"\n[ERROR] app.py not found at {app_py}")
            return False
        
        print(f"[OK] Found app.py")
        
        # Clean previous builds
        print("\n[CLEANING] Previous build artifacts...")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        if build_dir.exists():
            shutil.rmtree(build_dir)
        print("[OK] Cleaned")
        
        # Build command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name=SONY_Credentials',
            '--onefile',
            '--windowed',
            '--add-data=templates:templates',
            '--add-data=branding:branding',
            '--add-data=templates/Credential_Template.xlsx:templates',
            '--collect-all=flask',
            '--collect-all=reportlab',
            '--collect-all=chardet',
            '--hidden-import=flask',
            '--hidden-import=pandas',
            '--hidden-import=openpyxl',
            '--hidden-import=reportlab',
            '--hidden-import=requests',
            '--hidden-import=chardet',
            '--distpath=dist',
            '--workpath=build',
            str(app_py)
        ]
        
        # Add icon if it exists
        if icon_file.exists():
            cmd.insert(-1, f'--icon={icon_file}')
            print(f"[OK] Using icon: {icon_file}")
        
        # Run PyInstaller
        print("\n[BUILDING] Creating executable...")
        print("This may take 2-5 minutes...\n")
        
        result = subprocess.run(cmd, cwd=str(project_root))
        
        if result.returncode != 0:
            print("\n[ERROR] Build failed")
            return False
        
        # Check if exe was created
        exe_file = dist_dir / 'SONY_Credentials.exe'
        if not exe_file.exists():
            print(f"\n[ERROR] Executable not found at {exe_file}")
            return False
        
        # Get file size
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        
        print("\n" + "="*60)
        print("  BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\n[OK] Executable created: {exe_file}")
        print(f"[OK] Size: {size_mb:.1f} MB")
        print(f"\n[OK] Ready to use!")
        print(f"[OK] Next step: Test the exe or build Windows installer")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
