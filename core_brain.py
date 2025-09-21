import requests
from config import GROQ_API_KEY

def analyze_code(diff_text):
    """Sends code diff to Groq API for detailed review."""
    prompt = f"""
    **Role**: Senior Code Reviewer
    **Task**: Analyze the code diff thoroughly. Classify the type of change, provide a walkthrough, overall rating, and detailed feedback with impacts and priorities.
    Focus on:
    - Code structure and organization
    - Adherence to coding standards (e.g., PEP8 for Python, Swift best practices)
    - Potential bugs, edge cases, and logical errors
    - Performance optimizations
    - Security vulnerabilities
    - Readability and maintainability

    **Rules**:
    1. ALWAYS start with 'Rating: <NUMBER>/10' where NUMBER is from 1 to 10 based on overall quality. Do not use N/A.
    2. Classify the primary type of change (e.g., Feature Addition, Bug Fix, Refactor, Dependency Update, Documentation).
    3. Provide a brief code walkthrough summarizing the changes step-by-step, referencing files and approximate line numbers from the diff hunks.
    4. Include at least one positive feedback point.
    5. For line-specific feedback: Select the top 5 most important changed lines or hunks. For each:
       - Specify the file and lines (e.g., file.swift:10-15)
       - Quote the line(s) with context (+ for added, - for removed)
       - Describe the type of change (Addition, Removal, Modification)
       - Provide analysis/explanation
       - Suggest improvements if needed
       - Describe the impact if the suggestion is followed (e.g., Improves security, Reduces complexity)
       - Rate the priority of the suggestion (High, Medium, Low)
       - Provide a suggested comment for developers to post as a review comment
    6. Provide 3-5 general feedback points, each with potential impact and priority.
    7. Be thorough, critical, but constructive. Assume the diff is complete even if truncated.
    8. Output in Markdown format suitable for a GitHub README-style comment. Use HTML anchors for each line-specific feedback section (e.g., <a name="feedback-1"></a>).
    9. STRICTLY follow the output format. Do not add extra text outside the format.

    **Code Diff**:
    ```diff
    {diff_text[:6000]}
    ```

    **Output Format** EXACTLY:
    Rating: <NUMBER>/10

    # 🤖 AI PR Review

    ## Overall Rating
    <NUMBER>/10

    ## Change Type
    <Primary type, e.g., Refactor>

    ## Code Walkthrough
    <Step-by-step summary with file and line references>

    ## Positive Aspects
    - <Point 1>
    - <Point 2 if any>

    ## Line-Specific Feedback
    <a name="feedback-1"></a>
    ### 1. File: <file> Lines: <lines>
    **Quote:**
    ```diff
    <QUOTE>
    ```
    **Change Type:** <Type>
    **Analysis:** <Explanation>
    **Suggestion:** <Improvement or "None needed">
    **Impact if Implemented:** <Description of benefits>
    **Priority:** <High/Medium/Low>
    **Suggested Comment:** <Concise comment for developers to post>

    <a name="feedback-2"></a>
    ### 2. ... (repeat for 5)

    ## General Feedback
    - **Point 1:** <Description>  
      **Impact:** <Benefits>  
      **Priority:** <High/Medium/Low>
    - **Point 2:** ...
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",  # Reverted to reliable model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
        print(f"❌ [DEBUG] API Response: {error_msg}")
        return f"❌ Error: Groq API call failed. {error_msg}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error: Groq API call failed. {e}"

def parse_llm_output(llm_output):
    """Extracts rating and feedback from LLM response."""
    if not llm_output or "❌ Error" in llm_output:
        return "N/A", llm_output
    
    lines = llm_output.strip().split('\n')
    rating = "N/A"
    if lines and lines[0].startswith('Rating:'):
        rating = lines[0].replace('Rating:', '').strip()
    
    feedback = llm_output.strip()
    return rating, feedback