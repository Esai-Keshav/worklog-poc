#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()


def get_today_git_diff():
    """Gets the unified diff of all commits pushed in the last 24 hours."""
    try:
        # Fetch commits from the last 24 hours
        cmd = ["git", "log", "--since=24.hours.ago", "-p"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return None


def generate_worklog_from_diff(diff_text):
    if not diff_text or diff_text.strip() == "":
        print("No code changes found in the last 24 hours.")
        return None

    # Initialize Gemini Client (automatically uses GEMINI_API_KEY env variable)
    client = genai.Client()

    prompt = f"""
    You are an expert Technical Project Manager. Analyze this raw `git diff` from the last 24 hours.
    Generate an Executive Status Summary based ONLY on these changes.
    
    CRITICAL CONSTRAINT: The final output must be EXACTLY a 5-line Markdown list. No intro, no outro, no extra lines.
    
    Guidelines for the 5 lines:
    - Line 1: Date and top-line project health milestone achieved.
    - Line 2: Core backend feature/API update and its deployment readiness status.
    - Line 3: Core AI/Frontend system progression or critical adjustment.
    - Line 4: Primary bug fix, database stabilization, or performance win.
    - Line 5: Business impact summary or what this unblocks for next steps.

    Here is the raw git diff:
    \"\"\"
    {diff_text}
    \"\"\"
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text


if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY secret is missing.")
        exit(1)

    diff_data = get_today_git_diff()
    worklog = generate_worklog_from_diff(diff_data)

    print(worklog)

    if worklog:
        # Append the log to a central WORKLOG.md file
        with open("README.md", "a") as f:
            f.write("\n\n" + worklog)
        print("Worklog successfully generated and appended.")
