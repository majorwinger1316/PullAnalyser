```markdown
# PullAnalyser

A Flask-based webhook server that automates code reviews for GitHub pull requests (PRs) using the **Grok API**.  
It analyzes PR diffs, generates detailed feedback (code quality, bugs, optimizations), and posts comments directly on PRs.  
Deployed on **Render’s free tier**, it listens for webhooks at `/webhook` and uses environment variables for secure configuration.

---

## 📑 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Deploying to Render](#deploying-to-render)
- [Configuring GitHub Webhook](#configuring-github-webhook)
- [Troubleshooting](#troubleshooting)
  - [404 Not Found Error](#404-not-found-error)
  - [Comments Not Posting](#comments-not-posting)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Features
- **Automated Code Reviews**: Analyzes PR diffs using Grok API (`llama-3.1-8b-instant`) for structure, bugs, performance, and security.  
- **GitHub Integration**: Posts inline and main comments to PRs using a GitHub Personal Access Token (PAT).  
- **Multi-Platform Support**: Handles GitHub, GitLab, and Bitbucket webhooks (GitHub-focused).  
- **Secure Configuration**: Uses environment variables for secrets (`GROQ_API_KEY`, `WEBHOOK_SECRET`, `GITHUB_TOKEN`).  
- **Dockerized Deployment**: Runs on Render with a Dockerfile for consistent builds.  

---

## 🏗 Architecture
```

PullAnalyser/
├── app.py              # Flask app with /webhook endpoint
├── core\_brain.py       # Grok API for code analysis
├── git\_adapters.py     # GitHub/GitLab/Bitbucket webhook handlers
├── config.py           # Environment variable loader
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker setup for Render
├── .gitignore          # Ignores **pycache**, .env

````

---

## 📋 Prerequisites
- **Python**: 3.12+  
- **Docker**: For Render deployment  
- **GitHub Account**: With PAT (scopes: `repo`)  
- **Grok API Key**: From xAI  
- **ngrok**: For local webhook testing  
- **Render Account**: Free tier (no credit card required)  

---

## ⚡ Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/majorwinger1316/PullAnalyser.git
cd PullAnalyser
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
Flask==3.0.3
requests==2.32.3
gunicorn==22.0.0
```

### 3. Set Environment Variables

```bash
export GROQ_API_KEY="your_grok_api_key"
export WEBHOOK_SECRET="my_github_webhook_secret_123456!@#"
export GITHUB_TOKEN="your_github_token"  # Must have `repo` scope
```

Persist variables in `~/.zshrc` and reload:

```bash
source ~/.zshrc
```

Verify:

```bash
env | grep -E "GROQ_API_KEY|WEBHOOK_SECRET|GITHUB_TOKEN"
```

### 4. Run Locally

```bash
python app.py
```

Runs on: `http://0.0.0.0:5000`

### 5. Test with ngrok

```bash
ngrok http 5000
```

* Copy HTTPS URL (e.g., `https://abc123.ngrok-free.app`)
* Inspect traffic: [http://localhost:4040](http://localhost:4040)

---

## 🚀 Deploying to Render

### 1. Push to GitHub

Add `.gitignore`:

```
__pycache__/
*.pyc
.env
```

Push:

```bash
git push origin main
```

### 2. Create Web Service

* Sign in: [Render](https://render.com)
* **New → Web Service → Connect repo**
* Settings:

  * Name: `pullanalyser-1`
  * Runtime: **Docker**
  * Build: `docker build -t app .`
  * Start: `docker run -p 8080:8080 app`
  * Instance: Free
  * Environment Variables:

    * `GROQ_API_KEY` → Your Grok key
    * `WEBHOOK_SECRET` → `my_github_webhook_secret_123456!@#`
    * `GITHUB_TOKEN` → PAT with `repo` scope

Deploy (\~5-10 minutes).
App URL → `https://pullanalyser-1.onrender.com`

**Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

---

## 🔗 Configuring GitHub Webhook

1. Go to **Repo Settings → Webhooks → Add webhook**

   * **Payload URL**: `https://pullanalyser-1.onrender.com/webhook` (or ngrok URL)
   * **Content type**: `application/json`
   * **Secret**: `my_github_webhook_secret_123456!@#`
   * **Events**: `Pull requests` → (select *opened*)

2. Save & Test:

   * Open a PR in your repo (`F1Statistics`)
   * Check Render/ngrok logs
   * Verify PR comments

---

## 🛠 Troubleshooting

### ❌ 404 Not Found Error

* Issue: Root URL (`/`) returns 404
* Fix: Add a health route in `app.py`:

```python
@app.route('/')
def home():
    return 'PR Analyzer is running!', 200
```

Commit & redeploy:

```bash
git add app.py
git commit -m "Add root route"
git push origin main
```

---

### 📝 Comments Not Posting

* **Symptom**: Logs show `200 OK` but no PR comments
* **Causes & Fixes**:

  * **Invalid GITHUB\_TOKEN** → Regenerate with `repo` scope
  * **Repo Access** → Ensure token has access
  * **Non-opened PR** → Add support for `"synchronize"` events in `git_adapters.py`
  * **Grok API Failure** → Test with:

    ```bash
    curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
    ```

---

## 🔒 Security Notes

* **Revoke Exposed Secrets**:

  * GitHub → Developer settings → Tokens → Delete
  * Grok → Contact xAI support
* **Environment Variables**: Never hardcode secrets
* **Token Scopes**: `GITHUB_TOKEN` must include `repo` for private repos

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a PR

Testing PRs automatically triggers the analyzer.

---

## 📜 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

🔧 Powered by **CodeMate** & **Grok**

```

Would you like me to also **add badges** (e.g., Python, Flask, Docker, Render deploy, MIT License) at the top to make it look more professional?
```
