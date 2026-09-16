# IT Setup Checklist - SONY Credential Generator (reCAPTCHA v3)

## Quick Setup (Est. Time: 30 minutes)

### Phase 1: Get reCAPTCHA Keys (5-10 minutes)

- [ ] Visit: https://www.google.com/recaptcha/admin/create
- [ ] Sign in with Google account
- [ ] Create new site:
  - Label: `SONY Credential Generator`
  - Type: `reCAPTCHA v3`
  - Domain: `your-app.azurewebsites.net` (replace with actual Azure domain)
- [ ] Copy **Site Key** → save to secure location
- [ ] Copy **Secret Key** → save to secure location

**⚠️ IMPORTANT**: Secret Key is sensitive - store securely, never commit to git

---

### Phase 2: Azure App Service Configuration (10-15 minutes)

#### 2.1 Configure Environment Variables

1. Go to **Azure Portal**
2. Navigate to **App Service → Configuration → Application settings**
3. Click **+ New application setting** (add 2 new settings):

```
Name: RECAPTCHA_SITE_KEY
Value: [paste Site Key from Phase 1]
```

```
Name: RECAPTCHA_SECRET_KEY
Value: [paste Secret Key from Phase 1]
```

4. Click **Save** at the top
5. Wait for notification: "Successfully updated application settings"

#### 2.2 Check Existing Settings

- [ ] Verify `SCM_DO_BUILD_DURING_DEPLOYMENT` is set to `true`
- [ ] Verify `WEBSITE_RUN_FROM_PACKAGE` is NOT set (or set to 0)
- [ ] Verify Python version is 3.8+ (Advanced Tools → Runtime versions)

---

### Phase 3: Deploy Application Files (5-10 minutes)

Choose ONE deployment method:

#### Option A: ZIP Deploy (Easiest)
1. Extract `sony_credentials_deployment_recaptcha.zip`
2. Go to **App Service → Deployment Center**
3. Select **Manual deployment → ZIP**
4. Upload the extracted folder contents
5. Monitor: **Deployment Center → Deployments**

#### Option B: Azure CLI
```bash
az webapp up --name <your-app-name> --resource-group <resource-group>
```

#### Option C: Git/GitHub
1. Connect repository to Deployment Center
2. Push files to main branch
3. Automatic deployment triggers

---

### Phase 4: Verify Deployment (5 minutes)

1. Go to **App Service → Restart** and click **Restart**
2. Wait 30-60 seconds for restart to complete
3. Open application: `https://your-app.azurewebsites.net`

**Test File Upload**:
- [ ] Download template file
- [ ] Upload template with sample data
- [ ] Verify "File validated successfully" message
- [ ] Check browser console (F12) for no errors

**Test Credential Generation**:
- [ ] Select event type (Summer/Winter/Fall/Bowling)
- [ ] Click "Generate Credentials"
- [ ] Verify PDF downloads successfully
- [ ] Check PDF renders correctly

---

### Phase 5: Monitor Logs (First 24 hours)

#### Enable Application Insights (Recommended)
1. **App Service → Monitoring → Application Insights**
2. Click **Turn on Application Insights**
3. Create new resource or link existing one
4. Wait 2-3 minutes for connection

#### View Logs
- **Real-time**: App Service → Log stream
- **Detailed**: Application Insights → Logs (search for errors)
- **Failures**: Look for `"reCAPTCHA verification error"` or `"RECAPTCHA_SECRET_KEY not configured"`

---

## Post-Deployment Checklist

### Security

- [ ] Confirm HTTPS is enforced (HTTPS Only: ON)
- [ ] Verify reCAPTCHA keys are not exposed in logs
- [ ] Check no secrets are in connection strings
- [ ] Enable Azure AD authentication (if required)

### Performance

- [ ] Monitor CPU usage first 24 hours (should be <30%)
- [ ] Monitor memory usage (should be stable)
- [ ] Check response times in Application Insights

### Data

- [ ] Temporary files are cleaned up after downloads
- [ ] No uploaded Excel files persist in storage
- [ ] No PDF files stored permanently (current version)

---

## Troubleshooting During Setup

### Issue: "reCAPTCHA verification failed"

**Check**:
1. Application settings saved? (should show in Configuration)
2. App Service restarted? (Restart button)
3. Keys copied correctly? (no extra spaces)
4. Keys match reCAPTCHA admin console?

**Fix**:
```bash
# View current settings
az webapp config appsettings list --resource-group <rg> --name <app-name>

# If keys wrong, delete and re-add
az webapp config appsettings delete --name <app-name> --setting-names RECAPTCHA_SECRET_KEY
```

### Issue: "Warning: RECAPTCHA_SECRET_KEY not configured"

**Cause**: Environment variable not propagated yet

**Fix**:
1. Go to **App Service → Restart**
2. Wait 1 minute after restart
3. Refresh browser page
4. Check logs: `grep "Warning" <logfile>`

### Issue: Domain mismatch error from reCAPTCHA

**Fix**:
1. Go to [reCAPTCHA Console](https://www.google.com/recaptcha/admin/)
2. Select your site
3. Edit domain settings
4. Add your Azure domain
5. Save and wait 5 minutes

### Issue: File upload works but generation fails

**Check**:
1. Are both environment variables set? (SITE_KEY AND SECRET_KEY)
2. Is Secret Key (backend) set? (most common mistake)
3. Check logs for the actual error

**Fix**: Verify both keys in Azure Configuration

---

## Performance Tuning (Optional)

If experiencing slow responses:

1. **Increase App Service tier**:
   - Current: Basic (default)
   - Recommended: Standard S1 for production
   
2. **Enable auto-scaling**:
   - Go to **App Service Plan → Scale out**
   - Set minimum instances: 2
   - Set maximum instances: 4

3. **Enable Application Cache** (if using):
   - Consider Azure Cache for Redis
   - Cache template file paths

---

## Security Hardening (Optional but Recommended)

### 1. Azure AD Authentication
```python
# Add to app.py
from flask_aad import FlaskAAD
app_aad = FlaskAAD(app)
@app.route('/protected')
def protected():
    return "Only for authenticated users"
```

### 2. Network Security
- [ ] Enable firewall rules in Azure
- [ ] Restrict access to known IP ranges
- [ ] Use Private Endpoints for Azure Storage

### 3. Data Encryption
- [ ] Enable "Encryption in transit" (HTTPS)
- [ ] Enable "Encryption at rest" in Azure Storage
- [ ] Use Azure Key Vault for secrets

---

## Rollback Procedure (If Needed)

If deployment has critical issues:

1. **Option 1: Restore previous version**
   - **App Service → Deployment Center → Deployments**
   - Click previous successful deployment
   - Click **Redeploy**

2. **Option 2: Deploy older ZIP**
   - Upload `sony_credentials_deployment_final.zip` (previous version)
   - Restart app service

---

## Support Contacts & Resources

### Deployment Help
- Azure Documentation: https://docs.microsoft.com/azure/app-service
- Python on Azure: https://docs.microsoft.com/azure/developer/python

### reCAPTCHA Setup
- Google Console: https://www.google.com/recaptcha/admin/
- reCAPTCHA Docs: https://developers.google.com/recaptcha/docs/v3

### Application Logs
- Real-time: App Service → Log stream
- Detailed: Application Insights → Diagnostics

---

## Final Sign-Off

- [ ] All 5 phases completed
- [ ] Application loads at https://your-app.azurewebsites.net
- [ ] File upload test passed
- [ ] Credential generation test passed
- [ ] No errors in logs
- [ ] reCAPTCHA keys working (no "verification failed" messages)
- [ ] Ready for team training

**Date Deployed**: _______________

**Deployed By**: _______________

**Notes**: _______________________________________________

---

*For detailed configuration, see: DEPLOYMENT_GUIDE_RECAPTCHA.md*
