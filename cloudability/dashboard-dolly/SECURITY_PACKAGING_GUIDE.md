# Security & Packaging Guide

## ⚠️ CRITICAL: API Key Security

**NEVER distribute executables with API keys embedded!**

## Before Packaging

### Automatic Sanitization (Recommended)

The build script automatically removes API keys:

```bash
python3 build_executable.py
```

This will:
1. Scan all `Environments/*/config.json` files
2. Remove all API keys and credentials
3. Build the executable with clean configs

### Manual Sanitization

If you want to sanitize without building:

```bash
python3 sanitize_environments.py
```

This will:
- Remove `cldyKey`, `api_key`, `public_key`, `private_key` from all configs
- Create example configuration files
- Create a README for end users

## What Gets Packaged

The executable includes:
- ✅ Application code
- ✅ Empty environment config templates
- ✅ README files
- ❌ NO API keys
- ❌ NO credentials

## End User Setup

Users have two options:

### Option 1: Direct API Key Entry (Easiest)
1. Launch Dashboard Dolly
2. Go to Connections tab
3. Enter API key in "OR API Key" field
4. Click "Connect with Key"

**No configuration files needed!**

### Option 2: Environment Configuration Files
1. Launch Dashboard Dolly once
2. Click "Open Config Folder"
3. Create a new folder (e.g., "production")
4. Create `config.json`:
   ```json
   {
     "cldyKey": "their-api-key-here",
     "region": ""
   }
   ```
5. Restart Dashboard Dolly
6. Environment appears in dropdown

## Verification Checklist

Before distributing, verify:

- [ ] Run `python3 sanitize_environments.py`
- [ ] Check `Environments/` folder - no real API keys
- [ ] Build executable: `python3 build_executable.py`
- [ ] Test executable on clean system
- [ ] Verify no API keys in packaged files
- [ ] Include `END_USER_GUIDE.md` with distribution

## If You Accidentally Package API Keys

1. **DO NOT DISTRIBUTE** the executable
2. Run: `python3 sanitize_environments.py`
3. Rebuild: `python3 build_executable.py`
4. Verify the new build has no keys
5. Rotate any exposed API keys immediately

## Checking for API Keys in Built Package

### macOS
```bash
# Extract and search
cd dist
unzip -q DashboardDolly.zip
grep -r "cldyKey" DashboardDolly.app/
# Should return no results or only empty values
```

### Windows
```cmd
# Search in extracted folder
cd dist\DashboardDolly
findstr /s /i "cldyKey" *
# Should return no results or only empty values
```

## Best Practices

1. **Keep development and distribution separate**
   - Use a separate directory for building distributions
   - Never build from your active development environment

2. **Use version control wisely**
   - Add `Environments/*/config.json` to `.gitignore`
   - Only commit `.example` files

3. **Test on clean systems**
   - Always test the executable on a system without Python
   - Verify users can add their own credentials

4. **Document clearly**
   - Include `END_USER_GUIDE.md` with every distribution
   - Make it clear users need their own API keys

5. **Rotate keys after testing**
   - If you used real API keys for testing, rotate them
   - Never reuse test keys in production

## Security Incident Response

If API keys are accidentally distributed:

1. **Immediate Actions:**
   - Revoke/rotate all exposed API keys
   - Notify affected users
   - Remove distributed files

2. **Investigation:**
   - Identify which keys were exposed
   - Check for unauthorized usage
   - Document the incident

3. **Prevention:**
   - Update build process
   - Add additional verification steps
   - Train team on secure packaging

## Questions?

- How do I know if my build has API keys?
  → Run the verification commands above

- Can users share their configured executable?
  → NO! Each user needs their own API keys

- What if I need to pre-configure for a customer?
  → Use environment variables or secure key management, never embed keys

- How often should I rotate API keys?
  → Follow your organization's security policy, typically every 90 days

## Summary

✅ **DO:**
- Run sanitization before every build
- Test on clean systems
- Include user documentation
- Verify no keys in package

❌ **DON'T:**
- Distribute with embedded API keys
- Skip verification steps
- Reuse test API keys
- Share configured executables

---

**Remember: Security is everyone's responsibility!**