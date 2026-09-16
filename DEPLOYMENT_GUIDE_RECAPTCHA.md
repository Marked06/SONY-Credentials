# SONY Credential Generator - Deployment Guide (v2.0 with reCAPTCHA)

## What's Included in This Package

This deployment package contains the complete credential generation system with **reCAPTCHA v3 bot protection** enabled.

### Files & Directories:

```
├── app.py                              # Flask backend with reCAPTCHA verification
├── credential_generator_branded.py     # PDF generator with smooth gradients (1000 bands)
├── requirements.txt                    # Python dependencies (includes requests library)
├── templates/
│   ├── index.html                      # Frontend with reCAPTCHA integration
│   └── Credential_Template.xlsx        # Excel template for data entry
├── branding/
│   ├── Logo.png                        # Special Olympics logo
│   ├── SummerHeader.png                # Summer event header (Red gradient)
│   ├── SummerFooter.png                # Summer event footer
│   ├── WinterHeader.png                # Winter event header (Blue gradient)
│   ├── WinterFooter.png                # Winter event footer
│   ├── FallHeader.png                  # Fall event header (Orange gradient)
│   ├── FallFooter.png                  # Fall event footer
│   ├── BowlingHeader.png               # Bowling event header (Green gradient)
│   └── BowlingFooter.png               # Bowling event footer
└── Volunteers_Placeholder.xlsx         # Sample data file
```

## New Features in This Version

### ✅ reCAPTCHA v3 Bot Protection
- **Invisible protection** - Users won't see a checkbox, protection happens automatically
- **Score-based validation** - Evaluates user behavior (0.0 = bot, 1.0 = human, threshold set to 0.5)
- **Protected endpoints**:
  - `/api/validate-file` - File upload validation
  - `/api/generate-credentials` - PDF generation
- **Graceful degradation** - System works without keys (development) and activates protection once configured

### 📊 Enhanced Gradient Rendering
- **Smooth color transitions** - 1000 color bands for imperceptible gradients
- **Event-specific colors**:
  - Summer: Red (#ed2024)
  - Winter: Blue gradient (#4a7abd → #21409a)
  - Fall: Orange gradient (#fdc225 → #f26522)
  - Bowling: Green gradient (#9acc5c → #08753c)

### 🎨 Dynamic Layout
- Event name auto-sizing and 2-line support
- Auto-positioning role box below event name
- Dynamic name and detail text sizing
- Responsive credential card layout (3.85"W × 5.0"H, 4 per page)

---

## Pre-Deployment Setup

### Step 1: Create reCAPTCHA v3 Site Keys

1. Go to [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/create)
2. Sign in with your Google account (or create one if needed)
3. Create a new site:
   - **Label**: "SONY Credential Generator"
   - **reCAPTCHA type**: reCAPTCHA v3
   - **Domains**: Your Azure App Service domain (e.g., `sony-credentials.azurewebsites.net`)
   - Accept the reCAPTCHA terms
4. You'll receive:
   - **Site Key** (public key for frontend)
   - **Secret Key** (private key for backend verification)
5. **Keep these keys safe** - you'll need them in the next step

### Step 2: Deploy to Azure App Service

1. **Extract the ZIP file** to your local machine or deployment location
2. **Update Azure Configuration** - In Azure Portal:
   - Go to: **App Service → Configuration → Application settings**
   - Add two new application settings:
     ```
     RECAPTCHA_SITE_KEY = [paste your Site Key here]
     RECAPTCHA_SECRET_KEY = [paste your Secret Key here]
     ```
   - Click **Save**

3. **Install dependencies** (in Azure deployment):
   ```bash
   pip install -r requirements.txt
   ```

4. **Deploy files** to Azure App Service using one of these methods:
   - **Azure Portal**: App Service → Deployment Center → Connect to GitHub/Azure Repos
   - **Azure CLI**: `az webapp up --name <app-name>`
   - **ZIP deployment**: Upload the extracted folder contents

5. **Restart the App Service** after deployment
   - Azure Portal → App Service → Restart

### Step 3: Verify Deployment

1. **Open the application** in your browser:
   ```
   https://sony-credentials.azurewebsites.net
   ```

2. **Test the file upload**:
   - Download the template: `Credential_Template.xlsx`
   - Add sample participant data
   - Upload the file - reCAPTCHA validation occurs silently
   - If validation fails, check browser console for errors

3. **Test credential generation**:
   - Fill in event details (Event Name, select Event Type)
   - Click "Generate Credentials"
   - reCAPTCHA token is collected and sent to backend
   - PDF should download successfully

4. **Monitor errors** (if any):
   - Azure Portal → App Service → Monitoring → Log stream
   - Look for messages like:
     - `"reCAPTCHA verification error"` - Backend issue
     - `"Warning: RECAPTCHA_SECRET_KEY not configured"` - Missing configuration

---

## System Requirements

### Environment
- **Python**: 3.8+
- **Framework**: Flask 2.3.3
- **Web Server**: Gunicorn 21.2.0
- **Database**: None required (stateless system)
- **Storage**: Temporary file uploads (cleaned up after generation)

### Dependencies (installed automatically)
- `Flask==2.3.3` - Web framework
- `pandas==2.2.0` - Excel data processing
- `openpyxl==3.1.2` - Excel file handling
- `reportlab==4.0.9` - PDF generation
- `Pillow==10.1.0` - Image processing
- `python-dateutil==2.8.2` - Date utilities
- `gunicorn==21.2.0` - WSGI server
- `requests==2.31.0` - **NEW** - reCAPTCHA API calls

### Network Access Required
- **Outbound to Google reCAPTCHA API**: `https://www.google.com/recaptcha/api/siteverify`
  - Required for bot verification
  - Typical response time: <100ms

---

## Configuration Reference

### Environment Variables

```bash
# reCAPTCHA Configuration (REQUIRED for bot protection)
RECAPTCHA_SITE_KEY="<public-key-from-google>"
RECAPTCHA_SECRET_KEY="<secret-key-from-google>"

# Optional - Advanced Configuration
RECAPTCHA_THRESHOLD=0.5  # Score threshold (default: 0.5, range: 0.0-1.0)
                         # Higher = stricter bot protection
                         # 0.0 = allow all, 1.0 = block all
```

### Flask Configuration (in app.py)
```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
RECAPTCHA_THRESHOLD = 0.5               # Default score threshold
```

---

## How reCAPTCHA v3 Works

### For Users
- **Transparent**: No captcha checkbox, no UI change
- **Automatic**: Protection runs silently in background
- **Smart**: Learns from genuine usage patterns

### Behind the Scenes
1. User initiates file upload or credential generation
2. `getReCaptchaToken()` function calls Google's API
3. Google analyzes user behavior → returns score (0.0-1.0)
4. Frontend sends score to backend with request
5. Backend validates score against threshold (0.5)
6. If score ≥ 0.5: Request proceeds; If score < 0.5: Request rejected

### What It Protects Against
- Automated bulk uploads
- Bot-driven API abuse
- Credential harvesting attempts
- DoS attacks targeting file processing

### What It Doesn't Protect
- SQL injection - **Use parameterized queries** (pandas handles this)
- XSS attacks - **Sanitize user input** (Flask templates auto-escape)
- Unauthorized access - **Implement Azure AD authentication**
- Data at rest - **Encrypt Excel uploads** in Azure Storage

---

## Troubleshooting

### Issue: "reCAPTCHA verification failed" message

**Cause**: Invalid site key or misconfigured secret key

**Solution**:
1. Verify keys match Google reCAPTCHA admin console
2. Check Azure Configuration settings (correct spelling, no extra spaces)
3. Restart the app service
4. Check browser console (F12 → Console tab) for JavaScript errors

### Issue: File uploads work but credential generation fails with reCAPTCHA error

**Cause**: reCAPTCHA validation enabled for generation but not for upload

**Solution**:
- This is expected behavior - upload may work without full reCAPTCHA (depends on Google's risk assessment)
- Check Azure logs for specific error message
- Ensure RECAPTCHA_SECRET_KEY is properly configured

### Issue: "Warning: RECAPTCHA_SECRET_KEY not configured"

**Cause**: Environment variable not set in Azure

**Solution**:
1. Go to Azure Portal → App Service → Configuration
2. Add the missing environment variables
3. Restart the app service
4. Refresh the page

### Issue: reCAPTCHA works locally but not in Azure

**Cause**: Domain mismatch between reCAPTCHA console and Azure domain

**Solution**:
1. Go to [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/)
2. Edit the site settings
3. Add your Azure domain: `your-app.azurewebsites.net`
4. Save and wait 5 minutes for propagation

---

## Security Checklist

### Implemented (This Version)
- ✅ reCAPTCHA v3 bot protection (file upload + generation)
- ✅ File type validation (.xlsx/.xls only)
- ✅ Max file size enforcement (50MB limit)
- ✅ Excel column validation
- ✅ Data quality warnings

### To Implement (IT Team Responsibility)
- ⬜ Azure AD authentication (organizational accounts only)
- ⬜ HTTPS/TLS encryption (Azure automatically provides)
- ⬜ Azure Storage encryption for temporary files
- ⬜ Request logging and audit trails
- ⬜ IP allowlisting (if needed)
- ⬜ Database encryption for credential repository
- ⬜ GDPR/FERPA compliance for data retention

---

## Key Changes from Previous Version

| Feature | Before | Now |
|---------|--------|-----|
| Bot Protection | None | reCAPTCHA v3 ✨ |
| Gradient Smoothness | 40-500 bands | 1000 bands |
| reCAPTCHA Library | - | requests==2.31.0 |
| Frontend Integration | Manual validation | Automatic token collection |
| Graceful Degradation | N/A | Works without keys (dev) |

---

## File Upload Specifications

### Excel Template Format
- **Columns Required** (case-sensitive):
  - `Name first` - Participant's first name
  - `Name last/family` - Participant's last name
  - `Role` - Position/role (e.g., "Athlete", "Coach", "Volunteer")
  - `Sports` - Sport/activity name
  - `Delegation` - Region/delegation name

### File Requirements
- **Format**: .xlsx or .xls (Excel files only)
- **Max Size**: 50 MB
- **Minimum Records**: 1
- **Empty Cells**: Allowed but flagged in validation warnings

### Example Row
```
| Name first | Name last/family | Role     | Sports    | Delegation |
|------------|------------------|----------|-----------|------------|
| John       | Smith           | Athlete  | Swimming  | Nassau     |
| Sarah      | Johnson         | Volunteer| Basketball| Suffolk    |
```

---

## Support & Questions

### For Issues:
1. Check the **Troubleshooting** section above
2. Review Azure Application Insights logs
3. Check browser console (F12) for frontend errors
4. Contact your IT team for Azure-specific issues

### For reCAPTCHA Setup:
- Google reCAPTCHA Documentation: https://developers.google.com/recaptcha/docs/v3
- reCAPTCHA Admin Console: https://www.google.com/recaptcha/admin/

### For Application Issues:
- Review the inline code comments in app.py
- Check Flask logs in Azure Log Stream
- Verify all dependencies installed: `pip list | grep -E "Flask|pandas|reportlab"`

---

## Next Steps

1. **Obtain reCAPTCHA keys** from Google (Step 1 above)
2. **Deploy to Azure** with environment variables configured (Step 2)
3. **Test the system** with sample data (Step 3)
4. **Monitor logs** during first week of use
5. **Train staff** on file format and filtering features
6. **Plan credential reprints** for lost/damaged credentials

---

## Version Information

- **Release**: v2.0 (with reCAPTCHA v3)
- **Date**: August 2026
- **Status**: Ready for Azure deployment
- **Tested**: File validation, PDF generation, filtering, sorting
- **reCAPTCHA**: v3 (invisible, score-based)

---

*Last Updated: August 25, 2026*
