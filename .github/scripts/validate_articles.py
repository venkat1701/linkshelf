#!/usr/bin/env python3
"""
validate_articles.py - Validates the format of article submissions
"""

import os
import re
import sys
import subprocess

def get_changed_files():
    """Get list of changed markdown files in the PR"""
    # For local testing, you can use:
    # return subprocess.run(["git", "diff", "--name-only", "HEAD^", "HEAD"], capture_output=True, text=True).stdout.splitlines()

    # In GitHub Actions, use the GITHUB_EVENT_PATH
    if "GITHUB_EVENT_PATH" in os.environ:
        import json
        with open(os.environ["GITHUB_EVENT_PATH"], 'r') as f:
            event = json.load(f)

        # Get PR number
        pr_number = event.get("pull_request", {}).get("number")
        if not pr_number:
            print("Not a pull request or couldn't determine PR number")
            return []

        # Use GitHub CLI to get changed files
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json", "files"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Error getting changed files: {result.stderr}")
            return []

        try:
            files_data = json.loads(result.stdout)
            return [file["path"] for file in files_data.get("files", [])]
        except json.JSONDecodeError:
            print(f"Error parsing JSON: {result.stdout}")
            return []
    else:
        # If not in GitHub Actions, use git diff (assumes you're on PR branch)
        base_branch = "main"  # Or whatever your base branch is
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"],
            capture_output=True, text=True
        )
        return [f for f in result.stdout.splitlines() if f.endswith('.md')]

def validate_article_format(file_path):
    """Validate the format of an article file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # Check for required sections
    required_sections = {
        "title": r'#.*\[(.*?)\]\((.*?)\)',
        "author": r'\*\*Author:\*\*\s*(.*?)[\n\r]',
        "date": r'\*\*Date:\*\*\s*(.*?)[\n\r]',
        "added_by": r'\*\*Added by:\*\*\s*(.*?)[\n\r]',
        "added_on": r'\*\*Added on:\*\*\s*(.*?)[\n\r]',
        "summary": r'(?:##\s*Summary|\*\*Summary:\*\*)(.*?)(?:##|\*\*Key Insights:\*\*)',
        "key_insights": r'(?:##\s*Key Insights|\*\*Key Insights:\*\*)(.*?)(?:##|\*\*Tags:\*\*)',
        "tags": r'\*\*Tags:\*\*\s*(.*?)$'
    }

    for section_name, pattern in required_sections.items():
        if not re.search(pattern, content, re.DOTALL | re.MULTILINE):
            errors.append(f"Missing or invalid '{section_name}' section")

    # Check for title format (must be Markdown link)
    title_match = re.search(r'#.*\[(.*?)\]\((.*?)\)', content)
    if title_match:
        title = title_match.group(1)
        url = title_match.group(2)
        if not url.startswith("http"):
            errors.append(f"Invalid URL format in title: {url}")

    # Check date format (YYYY-MM-DD)
    date_patterns = [r'\*\*Date:\*\*\s*(.*?)[\n\r]', r'\*\*Added on:\*\*\s*(.*?)[\n\r]']
    for pattern in date_patterns:
        date_match = re.search(pattern, content)
        if date_match:
            date_str = date_match.group(1).strip()
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                errors.append(f"Invalid date format: {date_str}. Should be YYYY-MM-DD")

    # Check tags format
    tags_match = re.search(r'\*\*Tags:\*\*\s*(.*?)$', content, re.MULTILINE)
    if tags_match:
        tags_str = tags_match.group(1).strip()
        if not re.match(r'^(#[\w-]+\s*)+$', tags_str):
            errors.append(f"Invalid tags format: {tags_str}. Tags should be space-separated and start with #")

    return errors

def main():
    # Get changed files
    changed_files = get_changed_files()

    # Filter for markdown files that might be articles
    exclude_paths = ["README.md", "CONTRIBUTING.md", "template/"]
    article_files = [f for f in changed_files if f.endswith('.md') and not any(exclude in f for exclude in exclude_paths)]

    if not article_files:
        print("No article files found in this PR")
        return 0

    # Validate each article
    error_count = 0
    for file_path in article_files:
        print(f"Validating {file_path}...")
        errors = validate_article_format(file_path)

        if errors:
            print(f"❌ Validation errors in {file_path}:")
            for error in errors:
                print(f"  - {error}")
            error_count += len(errors)
        else:
            print(f"✅ {file_path} passed validation")

    if error_count > 0:
        print(f"\nTotal validation errors: {error_count}")
        return 1
    else:
        print("\nAll articles passed validation!")
        return 0

if __name__ == "__main__":
    sys.exit(main())