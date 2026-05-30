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
        print(result.stdout)
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
    print(diff_text)

    prompt = f"""
    You are an expert technical manager. Analyze this raw `git diff` containing code changes made over the last 24 hours.
    Generate a clean, professional engineering daily worklog in Markdown format based ONLY on these changes.
    
    Guidelines:
    - Group items logically by feature or module.
    - Be specific: name exact functions, endpoints, or files modified.
    - Format with a clear heading for today's date: {datetime.now().strftime('%Y-%m-%d')}.
    - Do not output generic summaries. Explain the code logic changes.

    Here is the raw git diff:
    \"\"\"
    {diff_text}
    \"\"\"
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    print(response.text)
    return response.text


if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY secret is missing.")
        exit(1)

    print("Checking environment variables...")
    if "GEMINI_API_KEY" in os.environ:
        # Check if it exists but is accidentally empty/blank
        key_length = len(os.environ["GEMINI_API_KEY"])
        print(
            f"✅ GEMINI_API_KEY is PRESENT in the environment. String length: {key_length} characters."
        )
    else:
        print("❌ GEMINI_API_KEY is COMPLETELY MISSING from the environment.")
    # ----------------------

    if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"].strip():
        print("Error: GEMINI_API_KEY secret is missing or empty. Exiting script.")
        exit(1)

    diff_data = get_today_git_diff()
    worklog = generate_worklog_from_diff(diff_data)

    if worklog:
        # Append the log to a central WORKLOG.md file
        with open("WORKLOG.md", "a") as f:
            f.write("\n\n" + worklog)
        print("Worklog successfully generated and appended.")
