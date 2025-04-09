#!/usr/bin/env python3
"""
update_readme.py - Updates the README.md with recently added articles and statistics
"""

import os
import re
import subprocess
from datetime import datetime
import json
from collections import defaultdict

# Constants
RECENT_ARTICLES_COUNT = 5
README_PATH = "README.md"
RECENT_ARTICLES_MARKER = "## Recently Added Articles"
STATISTICS_MARKER = "## Statistics"
END_MARKER = ""  # empty line or next section marker

def find_all_article_files():
    """Find all markdown files that could contain articles"""
    # Exclude specific paths
    exclude_paths = ["README.md", "CONTRIBUTING.md", "template/"]

    # Find all markdown files
    cmd = ["find", ".", "-type", "f", "-name", "*.md"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Filter out excluded paths
    files = result.stdout.strip().split("\n")
    files = [f for f in files if f and not any(exclude in f for exclude in exclude_paths)]

    return files

def extract_article_info(file_path):
    """Extract article metadata from a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract article data
    article = {}

    # Title
    title_match = re.search(r'#.*\[(.*?)\]\((.*?)\)', content)
    if title_match:
        article['title'] = title_match.group(1)
        article['url'] = title_match.group(2)
    else:
        # This might not be an article file
        return None

    # Author
    author_match = re.search(r'\*\*Author:\*\*\s*(.*?)[\n\r]', content)
    if author_match:
        article['author'] = author_match.group(1).strip()

    # Date added
    added_date_match = re.search(r'\*\*Added on:\*\*\s*(.*?)[\n\r]', content)
    if added_date_match:
        article['added_on'] = added_date_match.group(1).strip()
        # Convert date string to date object for sorting
        try:
            article['date_obj'] = datetime.strptime(article['added_on'], '%Y-%m-%d')
        except ValueError:
            # If date format is different, use current date
            article['date_obj'] = datetime.now()
    else:
        # If no added date, use file modification time
        mod_time = os.path.getmtime(file_path)
        article['date_obj'] = datetime.fromtimestamp(mod_time)
        article['added_on'] = article['date_obj'].strftime('%Y-%m-%d')

    # Added by
    added_by_match = re.search(r'\*\*Added by:\*\*\s*(.*?)[\n\r]', content)
    if added_by_match:
        article['added_by'] = added_by_match.group(1).strip()

    # Publication date
    pub_date_match = re.search(r'\*\*Date:\*\*\s*(.*?)[\n\r]', content)
    if pub_date_match:
        article['pub_date'] = pub_date_match.group(1).strip()

    # Tags
    tags_match = re.search(r'\*\*Tags:\*\*\s*(.*?)$', content, re.MULTILINE)
    if tags_match:
        tags_str = tags_match.group(1).strip()
        article['tags'] = [tag.strip() for tag in tags_str.split('#') if tag.strip()]

    # File path for categorization
    article['path'] = file_path

    # Extract topic from path
    path_parts = file_path.split('/')
    if len(path_parts) >= 2:
        article['topic'] = path_parts[1]  # Assuming topics are first-level directories
        if len(path_parts) >= 3:
            article['subtopic'] = '/'.join(path_parts[2:-1])  # Join all intermediate directories

    return article

def format_recent_articles_section(articles):
    """Format the recent articles section for README"""
    if not articles:
        return f"{RECENT_ARTICLES_MARKER}\n\nNo articles added yet."

    section = f"{RECENT_ARTICLES_MARKER}\n\n"

    for article in articles:
        topic_path = article.get('topic', '')
        subtopic = article.get('subtopic', '')
        full_topic = f"{topic_path}/{subtopic}" if subtopic else topic_path

        section += f"### [{article['title']}]({article['url']})\n\n"
        if 'author' in article:
            section += f"**Author:** {article['author']}  \n"
        if 'pub_date' in article:
            section += f"**Date:** {article['pub_date']}  \n"
        if 'added_by' in article:
            section += f"**Added by:** {article['added_by']}  \n"
        section += f"**Added on:** {article['added_on']}  \n"
        section += f"**Category:** {full_topic}  \n"

        if 'tags' in article and article['tags']:
            section += f"**Tags:** {' '.join(['#' + tag for tag in article['tags']])}  \n"

        section += "\n"

    return section

def generate_statistics(articles):
    """Generate statistics about the repository"""
    stats = {
        'total_articles': len(articles),
        'latest_update': max([a['date_obj'] for a in articles]).strftime('%Y-%m-%d') if articles else 'N/A',
        'topics': defaultdict(int),
        'tags': defaultdict(int),
        'contributors': defaultdict(int)
    }

    for article in articles:
        # Count by topic
        topic = article.get('topic', 'Uncategorized')
        stats['topics'][topic] += 1

        # Count by contributor
        contributor = article.get('added_by', 'Unknown')
        stats['contributors'][contributor] += 1

        # Count tags
        for tag in article.get('tags', []):
            stats['tags'][tag] += 1

    # Format statistics section
    section = f"{STATISTICS_MARKER}\n\n"
    section += f"- **Total Articles:** {stats['total_articles']}\n"
    section += f"- **Last Updated:** {stats['latest_update']}\n"

    # Top topics
    section += "\n### Top Topics\n\n"
    top_topics = sorted(stats['topics'].items(), key=lambda x: x[1], reverse=True)[:5]
    for topic, count in top_topics:
        section += f"- {topic}: {count} articles\n"

    # Top contributors
    section += "\n### Top Contributors\n\n"
    top_contributors = sorted(stats['contributors'].items(), key=lambda x: x[1], reverse=True)[:5]
    for contributor, count in top_contributors:
        section += f"- {contributor}: {count} articles\n"

    # Top tags
    section += "\n### Popular Tags\n\n"
    top_tags = sorted(stats['tags'].items(), key=lambda x: x[1], reverse=True)[:10]
    for tag, count in top_tags:
        section += f"- #{tag}: {count} occurrences\n"

    return section

def update_readme_file(recent_articles_section, statistics_section):
    """Update the README.md file with recent articles and statistics"""
    with open(README_PATH, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Replace recent articles section
    pattern = f"{RECENT_ARTICLES_MARKER}.*?(?=^#|$)"
    replacement = recent_articles_section
    readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL | re.MULTILINE)

    # Replace statistics section
    pattern = f"{STATISTICS_MARKER}.*?(?=^#|$)"
    replacement = statistics_section
    readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL | re.MULTILINE)

    # Write updated content back to README
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def main():
    # Find all potential article files
    article_files = find_all_article_files()

    # Extract article information
    articles = []
    for file_path in article_files:
        article_info = extract_article_info(file_path)
        if article_info:
            articles.append(article_info)

    # Sort articles by date (newest first)
    articles.sort(key=lambda x: x['date_obj'], reverse=True)

    # Get recent articles
    recent_articles = articles[:RECENT_ARTICLES_COUNT]

    # Format sections
    recent_articles_section = format_recent_articles_section(recent_articles)
    statistics_section = generate_statistics(articles)

    # Update README
    update_readme_file(recent_articles_section, statistics_section)

    print(f"Updated README.md with {len(recent_articles)} recent articles and statistics")

if __name__ == "__main__":
    main()