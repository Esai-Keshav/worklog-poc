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
    
    CRITICAL STRUCTURE CONSTRAINT:
    Your output must start exactly with the heading: ## WorkLog for {datetime.now().strftime('%Y-%m-%d')}
    Directly below that heading, output exactly a 5-line Markdown list detailing the status updates. No introduction text, no conversational filler, and no outro.

    Guidelines for the 5 lines:
    - Line 1: Summary of top-line project status or milestones reached.
    - Line 2: Backend feature, endpoint development, or integration progress.
    - Line 3: AI pipeline adjustments, frontend features, or system workflow updates.
    - Line 4: Infrastructure optimization, database fixes, or critical bug resolution.
    - Line 5: Operational impact statement explaining what these changes unblock next.

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
