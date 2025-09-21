Flask PR Analyzer
 
A Flask-based webhook server that automates code reviews for GitHub pull requests (PRs) using the Grok API. It analyzes PR diffs, generates detailed feedback (code quality, bugs, optimizations), and posts comments to PRs. Deployed on Render’s free tier, it listens for webhooks at /webhook and uses environment variables for secure configuration.
Table of Contents

Features
Architecture
Prerequisites
Local Setup
Deploying to Render
Configuring GitHub Webhook
Troubleshooting
404 Not Found Error
Comments Not Posting


Security Notes
Contributing
License

Features

Automated Code Reviews: Analyzes PR diffs using Grok API (llama-3.1-8b-instant) for structure, bugs, performance, and security.
GitHub Integration: Posts inline and main comments to PRs using a GitHub Personal Access Token (PAT).
Multi-Platform Support: Handles GitHub, GitLab, and Bitbucket webhooks (GitHub-focused).
Secure Configuration: Uses environment variables for secrets (GROQ_API_KEY, WEBHOOK_SECRET, GITHUB_TOKEN).
Dockerized Deployment: Runs on Render with a Dockerfile for consistent builds.

Architecture
PullAnalyser/
├── app.py              # Flask app with /webhook endpoint
├── core_brain.py       # Grok API for code analysis
├── git_adapters.py     # GitHub/GitLab/Bitbucket webhook handlers
├── config.py           # Environment variable loader
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker setup for Render
├── .gitignore          # Ignores __pycache__, .env

Prerequisites

Python: 3.12+
Docker: For Render deployment
GitHub Account: With PAT (scopes: repo)
Grok API Key: From xAI
ngrok: For local webhook testing
Render Account: Free tier, no credit card needed

Local Setup

Clone the Repository:
git clone https://github.com/majorwinger1316/PullAnalyser.git
cd PullAnalyser


Install Dependencies:
pip install -r requirements.txt

requirements.txt:
Flask==3.0.3
requests==2.32.3
gunicorn==22.0.0


Set Environment Variables:
export GROQ_API_KEY="your_grok_api_key"
export WEBHOOK_SECRET="my_github_webhook_secret_123456!@#"
export GITHUB_TOKEN="your_github_token"  # Must have `repo` scope


Persist: Add to ~/.zshrc and run source ~/.zshrc.
Verify: env | grep -E "GROQ_API_KEY|WEBHOOK_SECRET|GITHUB_TOKEN".


Run Locally:
python app.py


Runs on http://0.0.0.0:5000.


Test with ngrok:

Install: brew install ngrok (macOS) or download from ngrok.com.
Start: ngrok http 5000.
Copy HTTPS URL (e.g., https://abc123.ngrok-free.app).
Inspect: http://localhost:4040.



Deploying to Render

Push to GitHub:

Ensure .gitignore:__pycache__/
*.pyc
.env


Push: git push origin main.


Create Web Service:

Sign in: render.com (GitHub login).
Dashboard > New > Web Service > Connect majorwinger1316/PullAnalyser.
Settings:
Name: pullanalyser-1
Runtime: Docker
Build: docker build -t app .
Start: docker run -p 8080:8080 app
Instance: Free
Environment Variables:
GROQ_API_KEY: Your Grok key
WEBHOOK_SECRET: my_github_webhook_secret_123456!@#
GITHUB_TOKEN: PAT with repo scope




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



Configuring GitHub Webhook

Add Webhook:

Go to majorwinger1316/F1Statistics (target repo) > Settings > Webhooks > Add webhook.
Payload URL: https://pullanalyser-1.onrender.com/webhook (or ngrok URL for local).
Content type: application/json.
Secret: my_github_webhook_secret_123456!@# (matches WEBHOOK_SECRET).
Events: Pull requests (select opened).
Save.


Test:

Create a PR in F1Statistics.
Check Render logs (Dashboard > Logs) or ngrok (http://localhost:4040).
Verify PR comments in GitHub.



Troubleshooting
404 Not Found Error

Issue: Accessing https://pullanalyser-1.onrender.com returns 404 Not Found because no / route exists.
Fix:
Add to app.py:@app.route('/')
def home():
    return 'PR Analyzer is running!', 200


Commit: git add app.py && git commit -m "Add root route" && git push origin main.
Redeploy: Render Dashboard > Manual Deploy.
Test: curl https://pullanalyser-1.onrender.com (should return PR Analyzer is running!).


Note: Use /webhook for actual functionality.

Comments Not Posting

Issue: Logs show 200 OK for /webhook, but no PR comments (e.g., Post comment status: 401, "Bad credentials").

Causes and Fixes:

Invalid GITHUB_TOKEN:
Regenerate: GitHub > Settings > Developer settings > Tokens (classic) > Generate new token > Scopes: repo.
Update:
Local: export GITHUB_TOKEN="new_token".
Render: Dashboard > pullanalyser-1 > Environment > Update GITHUB_TOKEN.


Test: curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user (should return majorwinger1316).


Repo Access: Ensure token has access to F1Statistics (public or repo scope for private).
Test: curl -X POST -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" -d '{"body":"Test comment"}' https://api.github.com/repos/majorwinger1316/F1Statistics/issues/3/comments (should return 201).


Non-opened PR: Code skips if action isn’t opened.
Fix: Support synchronize in git_adapters.py:if payload.get('action') not in ['opened', 'synchronize']:
    print(f"🔍 [DEBUG] Skipping: Action is '{payload.get('action')}'")
    return "Only processing opened or synchronized PRs"




Grok API Failure: If logs show LLM output: ❌ Error:
Test: curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models.
Update GROQ_API_KEY if 401.




Debug Locally:
python app.py
ngrok http 5000
curl -X POST https://your-ngrok-url.ngrok-free.app/webhook \
     -H "Content-Type: application/json" \
     -H "X-Hub-Signature-256: sha256=$(python -c "import hmac,hashlib; print(hmac.new(b'my_github_webhook_secret_123456!@#', b'{\"action\":\"opened\",\"pull_request\":{\"number\":3,\"diff_url\":\"https://api.github.com/repos/majorwinger1316/F1Statistics/pulls/3.diff\",\"comments_url\":\"https://api.github.com/repos/majorwinger1316/F1Statistics/issues/3/comments\",\"url\":\"https://api.github.com/repos/majorwinger1316/F1Statistics/pulls/3\"}}', hashlib.sha256).hexdigest())")" \
     -H "X-GitHub-Event: pull_request" \
     -d '{"action":"opened","pull_request":{"number":3,"diff_url":"https://api.github.com/repos/majorwinger1316/F1Statistics/pulls/3.diff","comments_url":"https://api.github.com/repos/majorwinger1316/F1Statistics/issues/3/comments","url":"https://api.github.com/repos/majorwinger1316/F1Statistics/pulls/3"}}'



Security Notes

Revoke Exposed Secrets: If GITHUB_TOKEN or GROQ_API_KEY was hardcoded, revoke:
GitHub: Settings > Developer settings > Tokens > Delete.
Grok: Contact xAI support.


Environment Variables: config.py uses os.environ.get for safety.
Token Scopes: GITHUB_TOKEN must have repo for private repos like F1Statistics.

Contributing

Fork, modify, and submit PRs to majorwinger1316/PullAnalyser.
Test PRs to trigger the analyzer.

License
MIT License. See LICENSE (create if missing).
Powered by CodeMate & Grok
