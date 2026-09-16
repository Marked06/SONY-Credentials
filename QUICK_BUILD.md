# 🚀 SONY Credentials - Quick Build Guide

## ONE-CLICK BUILD (Windows)

### Step 1: Download Everything
✓ You have: `SONY_Credentials_Package.zip`
✓ Extract to your computer

### Step 2: Run Build Script
**Double-click:** `BUILD_EXE.bat`

That's it! The script will:
1. Check for Python
2. Install all dependencies  
3. Build the executable
4. Show you where it is

### Step 3: Your Executable
Location: `dist/SONY_Credentials.exe`

Ready to use! No more setup needed.

---

## What You Get

```
SONY_Credentials/
├── BUILD_EXE.bat                    ← Run this to build
├── build_exe.py                     ← Build configuration
├── app.py                           ← Main application
├── credential_generator_branded.py  ← PDF engine
├── requirements.txt                 ← Dependencies
│
├── templates/
│   ├── index.html                   ← Live preview UI
│   └── Credential_Template.xlsx     ← Excel template
│
└── docs/
    ├── BUILD_EXE_QUICK_START.md     ← Detailed build guide
    ├── EXE_DEPLOYMENT_GUIDE.md      ← Distribution guide
    └── QUICK_START_PREVIEW.md       ← Feature guide
```

---

## Prerequisites

**On Your Windows Machine (one-time):**

1. **Python 3.12+** from python.org
   - Download installer
   - Run installer
   - CHECK: "Add Python to PATH" during install
   - Verify: Open Command Prompt, type `python --version`

That's all you need!

---

## Build Process

### Option A: Easy Way (Recommended)
```
1. Extract the package
2. Double-click BUILD_EXE.bat
3. Wait 2-3 minutes
4. Done! Your exe is in dist/ folder
```

### Option B: Manual Way
```
1. Open Command Prompt
2. cd C:\path\to\SONY_Credentials_Package
3. python build_exe.py
4. Wait 2-3 minutes
5. Done! Your exe is in dist/ folder
```

---

## Testing Your Exe

After build completes:

```
1. Go to: dist/ folder
2. Double-click: SONY_Credentials.exe
3. Wait 3-5 seconds
4. Browser opens automatically
5. You see the credential generator
6. Success! 🎉
```

---

## Troubleshooting

### "Python is not installed"
- Download Python from python.org
- Make sure to check "Add Python to PATH"
- Restart Command Prompt
- Try again

### "Module not found"
- Run: `pip install -r requirements.txt`
- Then: `python build_exe.py`

### Build takes very long
- Normal! First build takes 2-3 minutes
- Don't interrupt the process

### Antivirus blocks build
- Temporarily whitelist the build folder
- Run the build
- Remove whitelist afterward
- The exe is safe (built from your code)

---

## Next Steps

Once you have your `SONY_Credentials.exe`:

1. **Test it** on your Windows machine
2. **Test generating credentials** with sample Excel file
3. **Print a sample** to verify sizing
4. **Copy exe to distribution** (USB, email, network share)
5. **Distribute to staff** - they just double-click and go!

---

## File Sizes

| Item | Size |
|------|------|
| Package | ~50 MB (zipped) |
| After extraction | ~150 MB |
| Built exe | ~150-200 MB |
| Total disk needed | ~400 MB |

---

## Support

If you encounter issues:

1. Check TROUBLESHOOTING section above
2. Review `BUILD_EXE_QUICK_START.md` for detailed help
3. Review `EXE_DEPLOYMENT_GUIDE.md` for usage help

---

## Summary

**3 easy steps:**
1. Extract package
2. Double-click BUILD_EXE.bat
3. Get your exe in 2-3 minutes!

No Python knowledge needed. Just follow the prompts. 🚀
