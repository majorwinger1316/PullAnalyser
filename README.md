Flask PR Analyzer
A Flask-based webhook server that analyzes GitHub pull requests (PRs) using the Grok API to provide automated code reviews. It processes PR diffs, generates detailed feedback (e.g., code quality, bugs, optimizations), and posts comments to GitHub PRs. Deployed on Render’s free tier, it listens for webhook events at /webhook and uses environment variables for secure configuration.
Features

Webhook Listener: Handles GitHub, GitLab, and Bitbucket webhooks (currently focused on GitHub).
AI Code Review: Uses Grok API (llama-3.1-8b-instant) to analyze PR diffs and generate Markdown-formatted reviews.
GitHub Integration: Posts inline and main comments to PRs using a GitHub Personal Access Token.
Secure Setup: Secrets (e.g., GROQ_API_KEY, WEBHOOK_SECRET) stored as environment variables.
Dockerized Deployment: Runs on Render with a Dockerfile for consistent builds.

Project Structure
PullAnalyser/
├── app.py              # Flask app with webhook endpoint
├── core_brain.py       # Grok API integration for code analysis
├── git_adapters.py     # GitHub/GitLab/Bitbucket adapters for webhook handling
├── config.py           # Environment variable configuration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker setup for Render
├── .gitignore          # Ignores __pycache__, .env, etc.

Prerequisites

Python 3.12+
Docker (for deployment)
GitHub account with a Personal Access Token (PAT) with repo scope
Grok API key (from xAI)
ngrok (for local testing)
Render account (free tier, no credit card needed)

Setup Instructions
Local Setup

Clone the Repository:
git clone https://github.com/majorwinger1316/PullAnalyser.git
cd PullAnalyser


Install Dependencies:
pip install -r requirements.txt

Contents of requirements.txt:
Flask==3.0.3
requests==2.32.3
gunicorn==22.0.0


Set Environment Variables:
export GROQ_API_KEY="your_grok_api_key"
export WEBHOOK_SECRET="your_webhook_secret"
export GITHUB_TOKEN="your_github_token"  # Needs `repo` scope


Add to ~/.zshrc for persistence.
Verify: env | grep -E "GROQ_API_KEY|WEBHOOK_SECRET|GITHUB_TOKEN".


Run Locally:
python app.py


Runs on http://0.0.0.0:5000.


Test with ngrok:

Install ngrok: brew install ngrok (macOS) or download from ngrok.com.
Start: ngrok http 5000.
Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app).
Inspect requests: http://localhost:4040.



Deployment on Render

Push to GitHub:

Ensure .gitignore includes:__pycache__/
*.pyc
.env


Push: git push origin main.


Create Render Web Service:

Sign in: render.com (GitHub login, no credit card).
Dashboard > New > Web Service > Connect majorwinger1316/PullAnalyser.
Configure:
Name: pullanalyser-1
Runtime: Docker
Build Command: docker build -t app .
Start Command: docker run -p 8080:8080 app
Instance Type: Free
Environment Variables:
GROQ_API_KEY: Your Grok key
WEBHOOK_SECRET: Your webhook secret
GITHUB_TOKEN: GitHub PAT with repo scope




Deploy (~5-10 minutes).
URL: https://pullanalyser-1.onrender.com.


Dockerfile:
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]



GitHub Webhook Setup

Add Webhook:

GitHub > majorwinger1316/F1Statistics (or target repo) > Settings > Webhooks > Add webhook.
Payload URL: https://pullanalyser-1.onrender.com/webhook (or ngrok URL for local).
Content type: application/json.
Secret: Match WEBHOOK_SECRET from env vars.
Events: Pull requests (select opened).
Save.


Test Webhook:

Create a PR in majorwinger1316/F1Statistics.
Check Render logs (Dashboard > Logs) or ngrok (http://localhost:4040).
Look for comments on the PR.



Troubleshooting
404 Not Found on https://pullanalyser-1.onrender.com

Cause: No route defined for / (root). The app only responds to /webhook.
Fix:Add a root route in app.py:@app.route('/')
def home():
    return 'PR Analyzer is running!', 200


Commit: git add app.py && git commit -m "Add root route" && git push origin main.
Redeploy: Render Dashboard > Manual Deploy.
Test: curl https://pullanalyser-1.onrender.com (should return PR Analyzer is running!).



Comments Not Posting to PR

Symptoms: Logs show 200 OK for /webhook, but no comments in PR (e.g., logs show Post comment status: 401, "Bad credentials").
Causes and Fixes:
Invalid GITHUB_TOKEN:
Regenerate: GitHub > Settings > Developer settings > Tokens (classic) > Generate new token > Scopes: repo.
Update: export GITHUB_TOKEN="new_token" (local) or Render > Environment > Update GITHUB_TOKEN.
Test: curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user (should return your username).


Wrong Repo: Webhook targets F1Statistics, not PullAnalyser. Ensure token has access (public or repo scope for private).
Non-opened PR: Code only processes action: opened. Test with a new PR or modify git_adapters.py:if payload.get('action') not in ['opened', 'synchronize']:
    print(f"🔍 [DEBUG] Skipping: Action is '{payload.get('action')}'")
    return "Only processing opened or synchronized PRs"


Grok API Failure: If logs show LLM output: ❌ Error, verify GROQ_API_KEY:curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models


Update key if 401.





Other Issues

403 Forbidden: Signature mismatch. Ensure WEBHOOK_SECRET matches in Render and GitHub webhook settings.
Logs: Check Render (Dashboard > Logs) or ngrok (http://localhost:4040) for debug output (added in git_adapters.py).
Free Tier Sleep: Render sleeps after 15 minutes (1-2s wake-up). Retry requests if delayed.

Security Notes

Revoke Exposed Secrets: If you previously hardcoded GITHUB_TOKEN or GROQ_API_KEY, revoke them:
GitHub: Settings > Developer settings > Tokens > Delete.
Grok: Contact xAI support.


Use Environment Variables: config.py uses os.environ.get for safety.
Private Repos: Ensure GITHUB_TOKEN has repo scope for F1Statistics.

Contributing

Fork the repo, make changes, and submit a PR.
Ensure PRs trigger webhooks to test the analyzer.

License
MIT License. See LICENSE file (add if missing).
Powered by CodeMate & Grok
