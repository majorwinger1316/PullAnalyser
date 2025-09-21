import requests
import json
from core_brain import analyze_code, parse_llm_output

class BaseGitAdapter:
    def __init__(self, server_type):
        self.server_type = server_type
    
    def handle_webhook(self, payload):
        raise NotImplementedError
    
    def post_comment(self, comment_url, comment_body, headers):
        response = requests.post(comment_url, json={"body": comment_body}, headers=headers)
        return response.status_code == 201

    def post_inline_comments(self, review_url, comments, headers):
        raise NotImplementedError

class GitHubAdapter(BaseGitAdapter):
    def __init__(self, token):
        super().__init__('github')
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github+json'
        }
    
    def post_inline_comments(self, review_url, comments, headers):
        """Posts inline comments as part of a GitHub PR review."""
        review_body = {
            "body": "Automated AI PR Review",
            "event": "COMMENT",
            "comments": comments
        }
        response = requests.post(review_url, json=review_body, headers=headers)
        return response.status_code == 201
    
    def handle_webhook(self, payload):
        if payload.get('action') != 'opened':
            return "Only processing opened PRs"
        
        pr_info = payload['pull_request']
        diff_url = pr_info['diff_url']
        comment_url = pr_info['comments_url']
        review_url = f"{pr_info['url']}/reviews"
        diff_response = requests.get(diff_url, headers={'Accept': 'application/vnd.github.v3.diff'})
        diff_text = diff_response.text
        
        llm_output = analyze_code(diff_text)
        rating, feedback = parse_llm_output(llm_output)
        
        # Parse feedback to extract inline comments
        inline_comments = []
        lines = feedback.split('\n')
        current_feedback = None
        for line in lines:
            if line.startswith('<a name="feedback-'):
                current_feedback = line.split('"')[1]
            elif line.startswith('**Suggested Comment:**') and current_feedback:
                comment_text = line.replace('**Suggested Comment:**', '').strip()
                # Extract file and line from the feedback section
                for prev_line in lines[lines.index(line)::-1]:
                    if prev_line.startswith('### ') and 'File:' in prev_line:
                        file_line = prev_line.split('File: ')[1].split(' Lines: ')[0]
                        line_number = prev_line.split('Lines: ')[1].split(']')[0]
                        # Approximate line number (first line of range)
                        line_number = int(line_number.split('-')[0])
                        inline_comments.append({
                            "path": file_line,
                            "line": line_number,
                            "body": f"{comment_text} ([See review](#{current_feedback}))"
                        })
                        break
        
        # Post inline comments if any
        if inline_comments:
            self.post_inline_comments(review_url, inline_comments, self.headers)
        
        # Post main review comment
        comment_body = f"{feedback}\n\n*Powered by CodeMate & Grok*"
        self.post_comment(comment_url, comment_body, self.headers)
        return f"Posted review for PR #{pr_info['number']}"

class GitLabAdapter(BaseGitAdapter):
    def __init__(self, token):
        super().__init__('gitlab')
        self.headers = {
            'Private-Token': token,
            'Accept': 'application/json'
        }
    
    def handle_webhook(self, payload):
        if payload.get('object_kind') != 'merge_request':
            return "Only processing merge requests"
            
        mr_info = payload['object_attributes']
        diff_url = mr_info['diff_url']
        comment_url = f"{mr_info['url']}/discussions"
        
        diff_response = requests.get(diff_url, headers=self.headers)
        diff_text = diff_response.text
        
        llm_output = analyze_code(diff_text)
        rating, feedback = parse_llm_output(llm_output)
        
        comment_body = {
            "body": f"{feedback}\n\n*Powered by CodeMate & Grok*"
        }
        
        self.post_comment(comment_url, comment_body, self.headers)
        return f"Posted review for MR #{mr_info['iid']}"

class BitbucketAdapter(BaseGitAdapter):
    def __init__(self, key, secret):
        super().__init__('bitbucket')
        self.headers = {
            'Authorization': f'Bearer {key}',
            'Accept': 'application/json'
        }
    
    def handle_webhook(self, payload):
        pr_info = payload['pullrequest']
        diff_url = pr_info['links']['diff']['href']
        comment_url = pr_info['links']['comments']['href']
        
        diff_response = requests.get(diff_url, headers=self.headers)
        diff_text = diff_response.text
        
        llm_output = analyze_code(diff_text)
        rating, feedback = parse_llm_output(llm_output)
        
        comment_body = {
            "content": {
                "raw": f"{feedback}\n\n*Powered by CodeMate & Grok*"
            }
        }
        
        self.post_comment(comment_url, comment_body, self.headers)
        return f"Posted review for PR #{pr_info['id']}"