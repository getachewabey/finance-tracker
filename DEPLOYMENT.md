# Deployment Guide (Streamlit Community Cloud)

This app is ready to easily deploy on Streamlit Community Cloud.

## Prerequisites
- A GitHub account.
- This project pushed to a GitHub repository.
- A Supabase project (URL and Key).
- A Google Gemini API Key.

## Step-by-Step Instructions

### 1. Push Code to GitHub
Ensure this project is in a GitHub repository.
If you haven't initialized git yet:
```bash
git init
git add .
git commit -m "Initial commit"
# Link to your remote repo
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and Sign In.
2. Click **"New app"**.
3. Select your repository, branch (`main`), and Main file path (`app.py`).
   - *Note: If this project is in a subdirectory (e.g. `personal-finance-app/app.py`), specify that path.*

### 3. Configure Secrets
**CRITICAL**: Your app will fail to start if you don't set the secrets. Streamlit Cloud does NOT read `.streamlit/secrets.toml` from the repo (for security). You must set them in the dashboard.

1. Once the app starts deploying (or fails), click **"Manage app"** (bottom right) or go to **Settings** -> **Secrets**.
2. Paste the contents of your local `.streamlit/secrets.toml` into the secrets editor:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
GEMINI_API_KEY = "your-gemini-key-here"
```
3. Click **Save**.

### 4. Reboot
The app should automatically detect the new secrets and restart. If not, click **Reboot** in the "Manage app" menu.

## Troubleshooting
- **ModuleNotFoundError**: Ensure `requirements.txt` is in the root directory relative to where you told Streamlit your app lives.
- **Supabase Connection Error**: Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct in the Cloud Secrets.
- **Theme Issues**: The app uses a light/dark theme toggle. Standard Streamlit theme settings are in `.streamlit/config.toml` which is safe to commit.
