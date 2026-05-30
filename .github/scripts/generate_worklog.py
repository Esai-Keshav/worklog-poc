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
    You are an elite Technical Project Manager. Analyze this raw `git diff` containing code changes made over the last 24 hours.
    Generate a high-level, clean, professional Executive Status Summary in Markdown format based on these changes.
    
    Guidelines:
    - Keep it concise, high-level, and scannable for non-technical stakeholders.
    - Focus on *what* business features were advanced, completed, or fixed, and *why* it matters (the business impact).
    - Group items by operational features, milestones, or work streams (e.g., "Authentication System", "Payment Processing").
    - Do not paste raw code patterns or focus heavily on internal function syntax. Translate the diff into clear deliverables.
    - Format with a clear heading for today's date: {datetime.now().strftime('%Y-%m-%d')}.

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
