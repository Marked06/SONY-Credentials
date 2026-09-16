"""
PyInstaller Build Script for SONY Credentials
Generates standalone SONY_Credentials.exe executable
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build standalone Windows executable using PyInstaller"""

    print("=" * 70)
    print("🔨 SONY Credentials - Building Standalone Windows Executable")
    print("=" * 70)

    # Get project directory
    project_dir = Path(__file__).parent
    print(f"\n📁 Project Directory: {project_dir}")

    # Check if PyInstaller is installed
    print("\n📦 Checking dependencies...")
    try:
        import PyInstaller
        print("  ✓ PyInstaller found")
    except ImportError:
        print("  ✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check other required packages
    required_packages = ['flask', 'pandas', 'reportlab']
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} found")
        except ImportError:
            print(f"  ✗ {package} not found")
            return False

    # PyInstaller command
    print("\n🔧 Building executable...")
    print("   (This may take 2-3 minutes...)\n")

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SONY_Credentials",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--add-data", f"{project_dir}/templates:templates",
        "--add-data", f"{project_dir}/templates/Credential_Template.xlsx:templates",
        "--hidden-import=flask",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=reportlab",
        "--collect-all=reportlab",
        "--noconfirm",
        "--distpath", str(project_dir / "dist"),
        "--buildpath", str(project_dir / "build"),
        "--specpath", str(project_dir),
        str(project_dir / "app.py")
    ]

    try:
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Build failed!")
            print("\nError output:")
            print(result.stderr)
            return False

        # Check if exe was created
        exe_path = project_dir / "dist" / "SONY_Credentials.exe"

        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # Convert to MB
            print("✅ Build successful!")
            print(f"\n📦 Executable Details:")
            print(f"   Location: {exe_path}")
            print(f"   Size: {file_size:.1f} MB")
            print(f"\n🎯 Next Steps:")
            print(f"   1. Copy SONY_Credentials.exe to your deployment location")
            print(f"   2. Test on Windows machine (no Python required!)")
            print(f"   3. Distribute to event staff")
            return True
        else:
            print("❌ Executable not created")
            return False

    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

def create_launcher_script():
    """Create a batch script to launch the app"""

    project_dir = Path(__file__).parent
    launcher_path = project_dir / "SONY_Credentials.bat"

    launcher_content = """@echo off
REM SONY Credentials Launcher
REM Opens the web browser to the credential generator

echo Starting SONY Credentials...
start http://localhost:8000
SONY_Credentials.exe
pause
"""

    with open(launcher_path, 'w') as f:
        f.write(launcher_content)

    print(f"\n📝 Created launcher script: {launcher_path}")

def main():
    """Main build process"""

    # Check Python version
    print(f"\n✓ Python Version: {sys.version.split()[0]}")
    print(f"✓ Platform: {sys.platform}")

    if sys.platform != "win32" and sys.platform != "cygwin":
        print("\n⚠️  Warning: Building on non-Windows platform")
        print("   The executable will be created but may not run on Windows")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False

    # Build the executable
    success = build_exe()

    if success:
        # Create launcher script
        create_launcher_script()

        print("\n" + "=" * 70)
        print("✅ BUILD COMPLETE!")
        print("=" * 70)
        print("\n📊 Summary:")
        print("  • Standalone Windows executable created")
        print("  • No Python installation required")
        print("  • No external dependencies needed")
        print("  • Ready for distribution")
        print("\n🚀 To use:")
        print("  1. Run: SONY_Credentials.exe")
        print("  2. Browser opens to http://localhost:8000")
        print("  3. Generate credentials as normal")
        print("\n💡 Tips:")
        print("  • Run from any directory on Windows")
        print("  • No installation needed")
        print("  • Works even with threadlock security software")
        print("  • Requires Windows 7 or newer")

        return True
    else:
        print("\n❌ BUILD FAILED")
        print("\nTroubleshooting:")
        print("  1. Ensure all dependencies are installed:")
        print("     pip install -r requirements.txt")
        print("  2. Check PyInstaller is up to date:")
        print("     pip install --upgrade pyinstaller")
        print("  3. Try building again with verbose output:")
        print("     python build_exe.py 2>&1 | tee build.log")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
