# Employee Training Tracker - 24/7 Cloud Deployment

This app now supports:
- PostgreSQL in cloud via `DATABASE_URL`
- SQLite fallback for local usage
- Optional access code via `APP_ACCESS_CODE`

## 1) Prepare GitHub Repo

From project folder:

```powershell
git init
git add .
git commit -m "Training tracker cloud-ready"
```

Push to GitHub (create empty repo first):

```powershell
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## 2) Deploy on Render (Recommended)

1. Go to Render dashboard.
2. Create **PostgreSQL** service first.
3. Create **Web Service** from your GitHub repo.
4. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
5. Add environment variables:
   - `DATABASE_URL` = value from Render PostgreSQL (Internal Database URL)
   - `APP_ACCESS_CODE` = choose a strong passcode for your users
6. Deploy.

## 3) First-Run Data Initialization

- If database is empty and `training_db.xlsx` is in project root, app imports all three sheets.
- If Excel is missing, sample data is generated.

## 4) Share With Users

- Give users the Render URL.
- They enter `APP_ACCESS_CODE` once per session.

## 5) Local Run (Still Supported)

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Without `DATABASE_URL`, app uses `training_tracker.db` locally.

## 6) Security Notes

- Keep `APP_ACCESS_CODE` private.
- For enterprise-grade auth, put app behind SSO/identity proxy.
- Never commit secrets to Git.
