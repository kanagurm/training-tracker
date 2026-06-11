# Employee Training Tracker - Self-Hosting Guide
## Migrate from Streamlit Cloud to Office Windows VM

**For**: Non-Technical Users  
**Platform**: Windows Server or Windows 10/11 Virtual Machine  
**Time Required**: 1-2 hours  
**Difficulty**: Beginner-Friendly ✅

---

## Table of Contents

1. [What You'll Need](#what-youll-need)
2. [Understanding What We're Doing](#understanding-what-were-doing)
3. [Step 1: Prepare Your Windows VM](#step-1-prepare-your-windows-vm)
4. [Step 2: Install Python](#step-2-install-python)
5. [Step 3: Copy Application Files](#step-3-copy-application-files)
6. [Step 4: Install Application Dependencies](#step-4-install-application-dependencies)
7. [Step 5: Export Data from Neon](#step-5-export-data-from-neon)
8. [Step 6: Configure Local Database](#step-6-configure-local-database)
9. [Step 7: Test the Application](#step-7-test-the-application)
10. [Step 8: Run Application 24/7](#step-8-run-application-247)
11. [Step 9: Allow Other Users to Access](#step-9-allow-other-users-to-access)
12. [Step 10: Stop Using Streamlit Cloud](#step-10-stop-using-streamlit-cloud)
13. [Troubleshooting](#troubleshooting)
14. [Maintenance & Updates](#maintenance--updates)

---

## What You'll Need

### Required Access & Resources

- [ ] **Windows VM** with:
  - Windows Server 2016+ OR Windows 10/11
  - At least 4GB RAM
  - At least 10GB free disk space
  - Administrator access (ability to install programs)
  
- [ ] **Network Access**:
  - VM can access the internet (for installation)
  - Other users on same office network can reach the VM
  - VM's IP address or computer name (ask IT if unsure)

- [ ] **Your Laptop/Desktop**:
  - Access to the folder: `C:\Users\gt102120\Downloads\TrainingTracker`
  - Ability to connect to the VM (Remote Desktop)

- [ ] **Accounts & Passwords**:
  - Streamlit Cloud login (to export data)
  - Gmail account with App Password (for emails to work)

### Optional but Helpful

- [ ] IT department contact (in case you need firewall help)
- [ ] Notepad open (to write down IP addresses, passwords)

---

## Understanding What We're Doing

### Current Setup (Cloud-Based)
```
Your Browser → Internet → Streamlit Cloud → Neon Database (PostgreSQL)
                                ↓
                          Email (Gmail)
```

**Problems**:
- Depends on internet connection
- Monthly usage limits
- Data stored outside your office

### New Setup (Self-Hosted)
```
Your Browser → Office Network → Windows VM → Local Database (SQLite)
                                     ↓
                               Email (Gmail)
```

**Benefits**:
- ✅ Works even if internet is down
- ✅ No usage limits
- ✅ Data stays on your office server
- ✅ Faster (no internet latency)
- ✅ Full control

---

## Step 1: Prepare Your Windows VM

### 1.1 Connect to Your VM

**If VM is Remote:**
1. Press `Windows Key + R`
2. Type: `mstsc`
3. Press Enter
4. Enter VM's IP address or name (example: `192.168.1.100` or `TRAINING-SERVER`)
5. Click "Connect"
6. Enter username and password
7. Click "OK"

**If VM is Your Local Machine:**
- Just log in normally

### 1.2 Create Application Folder

1. Open **File Explorer** (yellow folder icon on taskbar)
2. Navigate to `C:\` drive
3. Right-click in empty space → **New** → **Folder**
4. Name it: `TrainingTracker`
5. Press Enter

**Result**: You should now have `C:\TrainingTracker` folder

### 1.3 Check Internet Access

1. Open **Microsoft Edge** or **Internet Explorer**
2. Go to: `https://www.google.com`
3. If it loads, you have internet access ✅
4. If not, contact IT to enable internet on the VM

---

## Step 2: Install Python

### 2.1 Download Python Installer

1. Open web browser on the VM
2. Go to: `https://www.python.org/downloads/`
3. Click the big yellow button: **Download Python 3.11.x**
4. Save file to **Downloads** folder
5. Wait for download to complete

### 2.2 Run Python Installer

1. Go to **Downloads** folder
2. Double-click file: `python-3.11.x-amd64.exe`
3. **IMPORTANT**: Check the box: ☑ **Add Python to PATH**
4. Click: **Install Now**
5. Wait 2-3 minutes for installation
6. Click: **Close** when finished

### 2.3 Verify Python Installation

1. Press `Windows Key + R`
2. Type: `cmd`
3. Press Enter (a black window opens)
4. Type: `python --version`
5. Press Enter
6. You should see: `Python 3.11.x`

**If you see an error**: Python didn't install correctly. Restart VM and try Step 2 again.

---

## Step 3: Copy Application Files

### 3.1 Locate Files on Your Laptop

1. On your laptop (not the VM), open File Explorer
2. Navigate to: `C:\Users\gt102120\Downloads\TrainingTracker`
3. You should see files:
   - `app.py` (main application)
   - `requirements.txt` (list of dependencies)
   - `.streamlit` folder
   - Other files

### 3.2 Copy Files to VM

**Method A: Using Shared Network Drive**

1. On your laptop, right-click `TrainingTracker` folder
2. Select: **Copy**
3. Navigate to VM (via Remote Desktop)
4. Open `C:\TrainingTracker` on the VM
5. Right-click → **Paste**
6. Wait for all files to copy

**Method B: Using USB Drive** (if Remote Desktop clipboard doesn't work)

1. Copy `TrainingTracker` folder to USB drive
2. Plug USB into VM server
3. Copy from USB to `C:\TrainingTracker`

**Method C: Using Remote Desktop Clipboard**

1. In Remote Desktop connection, click **Show Options**
2. Go to **Local Resources** tab
3. Check: ☑ **Clipboard**
4. Connect to VM
5. Copy-paste normally

### 3.3 Verify Files Copied

1. On VM, open `C:\TrainingTracker`
2. You should see:
   - `app.py`
   - `requirements.txt`
   - `.streamlit` folder
   - `import_from_excel.py`
   - Other files

**Total size**: Should be around 50-100 MB

---

## Step 4: Install Application Dependencies

### 4.1 Open Command Prompt

1. Press `Windows Key`
2. Type: `cmd`
3. Right-click **Command Prompt**
4. Select: **Run as administrator**
5. Click "Yes" if prompted

### 4.2 Navigate to Application Folder

In the black command window, type exactly:

```
cd C:\TrainingTracker
```

Press Enter. You should see: `C:\TrainingTracker>`

### 4.3 Create Virtual Environment

Type:
```
python -m venv venv
```

Press Enter. Wait 30 seconds (this creates an isolated Python environment).

### 4.4 Activate Virtual Environment

Type:
```
venv\Scripts\activate
```

Press Enter. You should now see `(venv)` at the beginning of the line.

### 4.5 Install All Dependencies

Type:
```
pip install -r requirements.txt
```

Press Enter. Wait 2-5 minutes while it downloads and installs everything.

**You'll see lots of text scrolling**. This is normal!

**When complete**, you'll see: `Successfully installed streamlit-1.36.0 ...`

### 4.6 Verify Installation

Type:
```
streamlit --version
```

Press Enter. You should see: `Streamlit, version 1.36.x`

---

## Step 5: Export Data from Neon

### 5.1 Log Into Streamlit Cloud

1. On your laptop, go to: `https://share.streamlit.io/`
2. Sign in with your GitHub account
3. Find your Training Tracker app
4. Click **Settings** (gear icon)
5. Note down these values (write them down!):
   - `DATABASE_URL` (looks like `postgresql://user:pass@host/db`)

### 5.2 Export Data from Live App

**Option A: Use the Export Feature in Your App**

1. Go to your live app: `https://trainingtrackertennessee.streamlit.app/`
2. Click **📤 Export** in the sidebar
3. Click **Download Complete .xlsx**
4. Save file as: `backup_export.xlsx`
5. Keep this file safe!

**Option B: Connect to Neon Database Directly** (Advanced)

Skip this if you used Option A.

1. Install DBeaver on your laptop: `https://dbeaver.io/download/`
2. Create new connection → PostgreSQL
3. Paste the DATABASE_URL values (host, user, password, database)
4. Export all tables to Excel

### 5.3 Copy Excel Backup to VM

1. Copy `backup_export.xlsx` to the VM
2. Place it in: `C:\TrainingTracker\`

---

## Step 6: Configure Local Database

### 6.1 Create Configuration File

1. On VM, open Notepad (Start → Notepad)
2. Click File → New
3. Type exactly:

```
[server]
headless = true
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false
```

4. Click File → Save As
5. Navigate to: `C:\TrainingTracker\.streamlit\`
6. File name: `config.toml`
7. Save as type: **All Files**
8. Click Save

### 6.2 Create Secrets File (for Email)

1. In Notepad, click File → New
2. Type (replace with your actual Gmail info):

```
SMTP_USER = "your_email@gmail.com"
SMTP_PASS = "your_16_char_app_password"
```

3. Click File → Save As
4. Navigate to: `C:\TrainingTracker\.streamlit\`
5. File name: `secrets.toml`
6. Save as type: **All Files**
7. Click Save

**Important**: Use your Gmail App Password, not regular password!

### 6.3 Let App Use Local Database

The app will automatically create a local SQLite database file called `training_tracker.db` in `C:\TrainingTracker\` when you first run it.

**No DATABASE_URL needed** - just delete that line from `secrets.toml` if it exists.

---

## Step 7: Test the Application

### 7.1 Start the Application

1. Open Command Prompt as Administrator
2. Type:
```
cd C:\TrainingTracker
venv\Scripts\activate
streamlit run app.py
```

3. Press Enter

**You should see**:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 7.2 Open Application in Browser

1. On the VM, open web browser
2. Go to: `http://localhost:8501`
3. The Training Tracker should load!

**If it doesn't load**: See [Troubleshooting](#troubleshooting) section.

### 7.3 Import Your Data

1. In the app, click **📥 Import from Excel** in sidebar
2. Click **Browse files**
3. Select `backup_export.xlsx`
4. Select import mode: **Replace (clear table first)**
5. Check all three sheets: ☑ Employees ☑ Courses ☑ Training_Records
6. Click **Import Now**
7. Wait for success message

### 7.4 Verify Data Imported

1. Click **🏠 Dashboard** in sidebar
2. You should see your metrics (total records, completion rate, etc.)
3. Click **🔍 Browse Data** → verify employees, courses, records appear

**If data is missing**: Re-import the Excel file

### 7.5 Test Email Sending (Optional)

1. Click **📧 Email Reminders** in sidebar
2. Fill in manual reminder form
3. Enter your email address
4. Click **Send Reminder**
5. Check your inbox

**If email fails**: See [Troubleshooting](#troubleshooting) → Email Issues

---

## Step 8: Run Application 24/7

Right now, the app stops when you close the Command Prompt. Let's make it run continuously.

### Method A: Simple Batch File (Quick)

#### 8.1 Create Startup Script

1. Open Notepad
2. Type:
```batch
@echo off
cd C:\TrainingTracker
call venv\Scripts\activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
```

3. Save as: `C:\TrainingTracker\start_training_tracker.bat`
4. Save as type: **All Files**

#### 8.2 Create Shortcut in Startup Folder

1. Right-click `start_training_tracker.bat`
2. Select **Create shortcut**
3. Press `Windows Key + R`
4. Type: `shell:startup`
5. Press Enter (Startup folder opens)
6. Move the shortcut here
7. Restart VM

**Result**: App starts automatically when VM boots!

### Method B: Windows Service (Professional)

This keeps the app running even if you log out.

#### 8.3 Download NSSM (Service Manager)

1. Go to: `https://nssm.cc/download`
2. Download: **nssm 2.24**
3. Extract ZIP file
4. Copy `nssm.exe` to `C:\TrainingTracker\`

#### 8.4 Install as Windows Service

1. Open Command Prompt **as Administrator**
2. Type:
```
cd C:\TrainingTracker
nssm install TrainingTracker
```

3. Press Enter

A window opens:

4. **Path**: Click Browse → Select `C:\TrainingTracker\venv\Scripts\streamlit.exe`
5. **Startup directory**: `C:\TrainingTracker`
6. **Arguments**: `run app.py --server.port 8501 --server.address 0.0.0.0`
7. Click **Install service**

#### 8.5 Start the Service

In Command Prompt:
```
nssm start TrainingTracker
```

**Check status**:
```
nssm status TrainingTracker
```

Should say: `SERVICE_RUNNING`

#### 8.6 Verify Service is Running

1. Press `Windows Key + R`
2. Type: `services.msc`
3. Press Enter
4. Find **TrainingTracker** in the list
5. Status should be: **Running**
6. Startup Type should be: **Automatic**

**Now the app runs 24/7** even if you log out!

---

## Step 9: Allow Other Users to Access

### 9.1 Find VM's IP Address

1. On VM, press `Windows Key + R`
2. Type: `cmd`
3. Press Enter
4. Type: `ipconfig`
5. Press Enter
6. Look for **IPv4 Address**: (example: `192.168.1.100`)
7. Write this down!

### 9.2 Test from Another Computer

1. On another computer **on the same office network**
2. Open web browser
3. Go to: `http://192.168.1.100:8501` (use your VM's IP)
4. Training Tracker should load!

**If it doesn't load**: Continue to firewall step below.

### 9.3 Allow Through Windows Firewall

**Only if users can't access from other computers:**

1. On VM, press `Windows Key`
2. Type: `Windows Defender Firewall`
3. Click **Advanced settings**
4. Click **Inbound Rules** (left sidebar)
5. Click **New Rule...** (right sidebar)
6. Select: **Port**
7. Click **Next**
8. Select: **TCP**
9. Specific local ports: `8501`
10. Click **Next**
11. Select: **Allow the connection**
12. Click **Next**
13. Check all boxes: ☑ Domain ☑ Private ☑ Public
14. Click **Next**
15. Name: `Training Tracker Access`
16. Click **Finish**

Now try accessing from another computer again.

### 9.4 Create Easy-to-Remember URL (Optional)

**Ask IT to**:
- Add DNS entry: `training-tracker.yourcompany.local` → VM's IP
- Or use VM's computer name: `http://TRAINING-SERVER:8501`

Then users can access via: `http://training-tracker.yourcompany.local:8501`

---

## Step 10: Stop Using Streamlit Cloud

### 10.1 Verify Everything Works Locally

Before shutting down cloud version, check:

- [ ] Can access app from VM: `http://localhost:8501` ✅
- [ ] Can access from other computers: `http://VM-IP:8501` ✅
- [ ] All data imported correctly ✅
- [ ] Email reminders work ✅
- [ ] App runs 24/7 (service or startup script) ✅

### 10.2 Update User Bookmarks

1. Send email to all users
2. New URL: `http://192.168.1.100:8501` (or your DNS name)
3. Ask them to update bookmarks
4. Give 1-week transition period

### 10.3 Shut Down Streamlit Cloud App

1. Go to: `https://share.streamlit.io/`
2. Find your app
3. Click **Settings** (gear icon)
4. Scroll to bottom
5. Click **Delete app**
6. Confirm deletion

**Your app is now fully self-hosted!** 🎉

### 10.4 Delete Neon Database (Optional)

1. Go to: `https://neon.tech/`
2. Sign in
3. Select your project
4. Settings → Delete Project
5. Confirm

**Saves your free tier quota for other projects**

---

## Troubleshooting

### Problem: "Python is not recognized"

**Solution**:
1. Reinstall Python
2. Make sure to check ☑ **Add Python to PATH**
3. Restart VM

---

### Problem: "streamlit: command not found"

**Solution**:
```
cd C:\TrainingTracker
venv\Scripts\activate
pip install streamlit
```

---

### Problem: App won't start - "Address already in use"

**Solution**:
Something else is using port 8501.

1. Open Command Prompt as Admin
2. Type: `netstat -ano | findstr :8501`
3. Find the PID number
4. Type: `taskkill /PID [number] /F`
5. Try starting app again

---

### Problem: Can't access from other computers

**Checklist**:
1. Firewall rule created? (Step 9.3)
2. VM's IP address correct?
3. Other computer on same network?
4. Try pinging VM: `ping 192.168.1.100`

**Solution**:
Ask IT to check network firewall/router settings.

---

### Problem: Email not sending

**Checklist**:
1. Using Gmail App Password (not regular password)?
2. `secrets.toml` file has correct credentials?
3. 2-Factor Authentication enabled on Gmail?

**Test**:
1. Open `C:\TrainingTracker\.streamlit\secrets.toml`
2. Verify `SMTP_USER` and `SMTP_PASS` are correct
3. No extra spaces or quotes

---

### Problem: Data not importing from Excel

**Solution**:
1. Check Excel file has sheets named exactly: `Employees`, `Courses`, `Training_Records`
2. Column names match expected format
3. No empty rows at top of sheets
4. Try import mode: **Replace** instead of Append

---

### Problem: App runs slow

**Possible Causes**:
1. VM has too little RAM (needs 4GB minimum)
2. Too many users accessing at once (add more RAM)
3. Large database (>100,000 records)

**Solutions**:
1. Close other programs on VM
2. Ask IT to increase VM RAM to 8GB
3. Archive old training records

---

### Problem: App stops after logging out

**Solution**:
You're using Method A (batch file). Use **Method B (Windows Service)** from Step 8.

---

## Maintenance & Updates

### Weekly Backups

**Every Monday**:
1. Go to app: `http://localhost:8501`
2. Click **📤 Export**
3. Download **Complete .xlsx**
4. Save as: `Backup_YYYY-MM-DD.xlsx`
5. Copy to: `\\fileserver\Backups\TrainingTracker\`

### Monthly Updates

**Check for updates**:
1. Check GitHub: `https://github.com/kanagurm/training-tracker`
2. If updates available:
   - Copy new files to `C:\TrainingTracker`
   - Restart service: `nssm restart TrainingTracker`

### Monitoring

**Daily Check** (automated):
- Open: `http://192.168.1.100:8501`
- If it loads → ✅ Running
- If error → Restart service

**Create batch file for quick check**:
```batch
@echo off
echo Checking Training Tracker...
nssm status TrainingTracker
pause
```

Save as: `C:\TrainingTracker\check_status.bat`

---

## Summary Checklist

Before considering migration complete:

- [ ] Python installed on VM
- [ ] All files copied to `C:\TrainingTracker`
- [ ] Dependencies installed via `pip install -r requirements.txt`
- [ ] Data exported from Neon and imported locally
- [ ] Email configured in `secrets.toml`
- [ ] App accessible from VM: `http://localhost:8501`
- [ ] App accessible from other computers: `http://VM-IP:8501`
- [ ] App runs 24/7 (Windows Service or Startup Script)
- [ ] Firewall allows port 8501
- [ ] Backup created and saved
- [ ] Users notified of new URL
- [ ] Streamlit Cloud app deleted
- [ ] Documentation saved in: `C:\TrainingTracker\SELF_HOSTING_GUIDE.md`

---

## Quick Reference

### Starting the App (Manual)
```
cd C:\TrainingTracker
venv\Scripts\activate
streamlit run app.py
```

### Stopping the App (Service)
```
nssm stop TrainingTracker
```

### Restarting the App (Service)
```
nssm restart TrainingTracker
```

### Checking Service Status
```
nssm status TrainingTracker
```

### Viewing Logs
Check: `C:\TrainingTracker\app.log` (if logging enabled)

### Access URLs
- On VM: `http://localhost:8501`
- From other computers: `http://[VM-IP]:8501`
- Example: `http://192.168.1.100:8501`

---

## Getting Help

### Self-Service
1. Check [Troubleshooting](#troubleshooting) section above
2. Review `USER_GUIDE.md` in TrainingTracker folder
3. Check GitHub Issues: `https://github.com/kanagurm/training-tracker/issues`

### IT Support
Contact your IT department for:
- VM access issues
- Network/firewall problems
- IP address or DNS setup
- Resource allocation (RAM/disk)

### Developer Support
For application bugs:
- Email: (add support email)
- GitHub: Open an issue with error screenshot

---

## Appendix: Advanced Configuration

### Using SQL Server Instead of SQLite

If you want to use Microsoft SQL Server:

1. Install SQL Server Express (free)
2. Create database: `TrainingTrackerDB`
3. Update `secrets.toml`:
```toml
DATABASE_URL = "mssql+pyodbc://username:password@localhost/TrainingTrackerDB?driver=ODBC+Driver+17+for+SQL+Server"
```
4. Install driver: `pip install pyodbc`

### Adding SSL Certificate (HTTPS)

Use IIS or Nginx as reverse proxy:
- Listens on port 443 (HTTPS)
- Forwards to localhost:8501
- Requires SSL certificate (free from Let's Encrypt)

### Performance Tuning

Edit `config.toml`:
```toml
[server]
maxUploadSize = 200
enableXsrfProtection = true

[runner]
magicEnabled = false
```

---

**Congratulations!** 🎉 

You've successfully migrated your Training Tracker from cloud to self-hosted!

Your app is now:
- ✅ Running 24/7 on your office VM
- ✅ Accessible to all employees on the network
- ✅ Fully under your control
- ✅ Free from usage limits

**Save this guide** for future reference and updates!

---

*Document Version: 1.0*  
*Last Updated: June 12, 2026*  
*For: Gainwell Technologies - Tennessee*
