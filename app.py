from flask import Flask, request, abort
import hmac
import hashlib
import json
import os
from git_adapters import GitHubAdapter, GitLabAdapter, BitbucketAdapter
from config import WEBHOOK_SECRET, GITHUB_TOKEN, GITLAB_TOKEN, BITBUCKET_KEY, BITBUCKET_SECRET

app = Flask(__name__)

def get_git_adapter(headers, payload):
    """Determine which git server sent the webhook and return appropriate adapter"""
    if 'X-GitHub-Event' in headers:
        return GitHubAdapter(GITHUB_TOKEN)
    elif 'X-Gitlab-Event' in headers:
        return GitLabAdapter(GITLAB_TOKEN)
    elif 'X-Hub-Signature' in headers and 'Bitbucket' in headers.get('User-Agent', ''):
        return BitbucketAdapter(BITBUCKET_KEY, BITBUCKET_SECRET)
    return None

def verify_signature(payload_body, signature_header, git_server):
    """Verify webhook signature based on git server type"""
    if not signature_header:
        print("❌ [DEBUG] No signature header received!")
        return False

    key = bytes(WEBHOOK_SECRET, 'utf-8')
    if git_server == 'github':
        expected_signature = hmac.new(key, payload_body, hashlib.sha256).hexdigest()
        expected_sig_full = f"sha256={expected_signature}"
    elif git_server == 'gitlab':
        expected_signature = hmac.new(key, payload_body, hashlib.sha1).hexdigest()
        expected_sig_full = expected_signature
    else:  # bitbucket
        expected_signature = hmac.new(key, payload_body, hashlib.sha256).hexdigest()
        expected_sig_full = expected_signature

    print(f"🔍 [DEBUG] Expected Signature: '{expected_sig_full}'")
    print(f"🔍 [DEBUG] Received Signature: '{signature_header}'")
    return hmac.compare_digest(expected_sig_full, signature_header)

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    print("\n--- NEW WEBHOOK REQUEST ---")
    
    payload_body = request.get_data()
    headers = request.headers
    
    # Determine git server and get appropriate adapter
    adapter = get_git_adapter(headers, payload_body)
    if not adapter:
        abort(400, description="Unsupported git server")
    
    # Verify signature
    signature_header = (headers.get('X-Hub-Signature-256') or 
                       headers.get('X-Gitlab-Token') or 
                       headers.get('X-Hub-Signature'))
    if not verify_signature(payload_body, signature_header, adapter.server_type):
        abort(403, description="Invalid webhook signature")
    
    # Process webhook
    payload = request.get_json()
    result = adapter.handle_webhook(payload)
    
    return {"status": "processed", "message": result}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Default to 5000 for EB
    app.run(debug=True, host='0.0.0.0', port=port)