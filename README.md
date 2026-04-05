# Nametag Demo Admin — Config Manager

A lightweight Flask web app for managing Google Sheets configuration files used by the Nametag n8n demo. **Zero cost. No Google Cloud account required.**

---

## What You're Deploying

A dark-themed admin page (matching Nametag's branding) with two sections:

- **Nametag Data Configuration** — full CRUD on your data sources sheet
- **Nametag Timecard CSV Configuration** — edit the timecard output format

It reads your public Google Sheets for free, and writes to them through a tiny (also free) Google Apps Script.

---

## FULL SETUP — 3 Steps (~15 minutes)

---

### STEP 1: Deploy the Apps Script Write Proxy (~5 min)

This is a small script that runs under your Google account and lets the web app write to your sheets. No API keys needed.

1. Open your browser and go to: **https://script.google.com**
   - You'll land on the Google Apps Script dashboard
   - If prompted, sign in with the same Google account that owns your sheets

2. Click the **"New project"** button (top left area)
   - A new script editor opens with some default code (`function myFunction()...`)

3. **Delete ALL the default code** in the editor (select all, then delete)

4. Open the file called `apps_script.js` from this repo (it's in the root folder)
   - Copy the ENTIRE contents of that file
   - Paste it into the Apps Script editor (replacing what you deleted)

5. **Rename the project** (optional but helpful):
   - Click "Untitled project" at the top left
   - Type: `Nametag Admin Proxy`
   - Hit Enter

6. **Save the script:**
   - Click the floppy disk icon, OR press `Ctrl+S` (Mac: `Cmd+S`)

7. **Deploy the script:**
   - Click the blue **"Deploy"** button (top right area)
   - Click **"New deployment"**

8. **Configure the deployment:**
   - Next to "Select type", click the **gear icon**
   - Select **"Web app"**
   - You'll see a form appear:
     - **Description:** type `Nametag Admin Proxy`
     - **Execute as:** leave as `Me (your-email@gmail.com)`
     - **Who has access:** change this to **`Anyone`**

9. Click the blue **"Deploy"** button

10. **Authorize the script:**
    - A popup says "Authorization required" — click **"Authorize access"**
    - Choose your Google account
    - You may see a "Google hasn't verified this app" warning:
      - Click **"Advanced"** (bottom left of the warning)
      - Click **"Go to Nametag Admin Proxy (unsafe)"**
      - Click **"Allow"**
    - This is safe — you wrote this script, it's running under your own account

11. **Copy the Web App URL:**
    - After authorizing, you'll see a "Deployment successfully updated" screen
    - There's a **"Web app" URL** that looks like:
      ```
      https://script.google.com/macros/s/AKfycbxSOME_LONG_STRING_HERE/exec
      ```
    - Click the **copy icon** next to it, or select and copy the full URL
    - **SAVE THIS URL** — you'll need it in Step 3

12. **Test it:**
    - Paste that URL into a new browser tab and hit Enter
    - You should see:
      ```
      {"status":"ok","message":"Nametag Admin write proxy is running."}
      ```
    - If you see that, you're golden. Move to Step 2.

---

### STEP 2: Push Files to GitHub (~5 min)

You need all the project files in a GitHub repo so Render can pull them.

#### 2A. Download the files

Download all the files from this package. You should have this folder structure:

```
nametag-admin/
├── app.py
├── apps_script.js
├── requirements.txt
├── render.yaml
├── .gitignore
├── README.md
└── templates/
    ├── base.html
    ├── index.html
    ├── data_config.html
    └── timecard_config.html
```

#### 2B. Create a new GitHub repo

1. Open your browser and go to: **https://github.com/new**
   - If not logged in, log in first

2. Fill out the form:
   - **Repository name:** `nametag-admin`
   - **Description:** `Nametag demo admin config manager`
   - **Visibility:** Select **Public**
   - **DO NOT** check "Add a README file" (we already have one)
   - **DO NOT** select a .gitignore template (we already have one)
   - **DO NOT** choose a license

3. Click the green **"Create repository"** button

4. You'll land on a page that says "Quick setup" with instructions. **Keep this page open** — you'll need the URL shown there.

#### 2C. Push the files (from your terminal)

Open a terminal (Terminal on Mac, Command Prompt or Git Bash on Windows) and run these commands one at a time:

```bash
# Navigate to where you downloaded the files
cd ~/Downloads/nametag-admin
# (adjust the path above to wherever your files are)

# Initialize git
git init

# Add all files
git add .

# Make the first commit
git commit -m "Nametag Admin config manager"

# Connect to your GitHub repo (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nametag-admin.git

# Push
git branch -M main
git push -u origin main
```

**If git asks for credentials:**
- Username: your GitHub username
- Password: use a Personal Access Token (NOT your GitHub password)
  - To create one: GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic) > Generate new token > check "repo" scope > Generate > copy the token and use it as your password

**Verify:** Go back to your browser and refresh the GitHub repo page. You should see all your files listed.

---

### STEP 3: Deploy to Render (~5 min)

1. Open your browser and go to: **https://dashboard.render.com**
   - Log in with the same account you use for your existing Nametag demo

2. Click **"New +"** (top right of the dashboard)

3. Click **"Web Service"**

4. **Connect your repo:**
   - If you haven't connected GitHub before, click "Connect GitHub" and authorize Render
   - You should see your repositories listed
   - Find **`nametag-admin`** and click **"Connect"** next to it

5. **Configure the service — fill in these fields exactly:**

   | Field | What to enter |
   |-------|--------------|
   | **Name** | `nametag-admin` |
   | **Region** | Same region as your existing Nametag demo (e.g., `Oregon (US West)`) |
   | **Branch** | `main` |
   | **Runtime** | `Python` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app` |

6. **Select the free tier:**
   - Scroll down to "Instance Type"
   - Click **"Free"**
   - (It says $0/month)

7. **Add the environment variable:**
   - Scroll down to the **"Environment Variables"** section
   - Click **"Add Environment Variable"**
   - Fill in:
     - **Key:** `APPS_SCRIPT_URL`
     - **Value:** paste the Web App URL you copied in Step 1 (the full `https://script.google.com/macros/s/...` URL)
   - That's the ONLY variable you need

8. Click the big blue **"Deploy Web Service"** button at the bottom

9. **Wait for the build:**
   - Render will show you a log of the build process
   - It takes about 1-2 minutes
   - When you see `==> Your service is live` in the log, you're done

10. **Your app is now live at:**
    ```
    https://nametag-admin.onrender.com
    ```
    (The exact URL is shown at the top of your Render service page)

---

## Verify Everything Works

1. Click your Render URL — you should see the dark-themed Nametag Admin dashboard with the badge icon in the top left

2. Click **"Nametag Data Configuration"**
   - You should see your 3 existing entries (Gsheet list DB1, Simulated DB2, cloud sim DB3)
   - Try clicking **Edit** on one, change the name, click **Save**
   - Go check the actual Google Sheet to confirm it updated

3. Click the back arrow to return to the dashboard

4. Click **"Nametag Timecard CSV Configuration"**
   - You should see the current values from row 2
   - Try changing a value and clicking **Save Changes**

---

## Troubleshooting

**"Could not read sheet" error:**
- Make sure both sheets are shared as "Anyone with the link can edit"
- Open each sheet in an incognito browser window to verify they're accessible

**"APPS_SCRIPT_URL is not set" error:**
- Go to Render Dashboard > your nametag-admin service > Environment
- Check that APPS_SCRIPT_URL is set and has the full URL

**"Write failed" error when saving:**
- Paste your Apps Script URL in a browser to verify it returns the "ok" JSON
- Make sure the Apps Script deployment has "Who has access" set to "Anyone"

**Page takes 30 seconds to load the first time:**
- Normal. Render free tier sleeps after 15 min of inactivity. First request wakes it up. After that it's fast until it sleeps again.
