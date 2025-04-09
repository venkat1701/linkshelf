# Contributing to Linkshelf

Thank you for considering contributing to our shared knowledge repository! This document outlines the process for adding new articles and maintaining our collective resource.

## Before You Begin

1. **Check Existing Content**: Browse the repository to ensure the article hasn't already been added.
2. **Find the Right Location**: Determine the appropriate topic (and subtopic if applicable) for your article.
3. **Create Folders if Needed**: If a suitable topic/subtopic doesn't exist, you can create it.

## Adding a New Article

### Step 1: Fork and Clone the Repository

1. Fork this repository to your GitHub account.
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/your-username/linkshelf.git
   cd linkshelf
   ```
3. Create a new branch for your contribution:
   ```bash
   git checkout -b add/article-name
   ```

### Step 2: Add Your Article

1. Navigate to the appropriate topic directory (or create it if needed).
2. Each article should be added to the README.md of the most specific relevant topic/subtopic.
3. Follow the standard format:

```markdown
### [Article Title](https://link-to-article)

**Author:** Name of author or publication  
**Date:** YYYY-MM-DD (publication date)  
**Added by:** Your Name  
**Added on:** YYYY-MM-DD (today's date)

**Summary:**  
A concise summary of the article's key points (3-5 sentences). Focus on the main takeaways and why this article is valuable.

**Key Insights:**
- First important insight or learning
- Second important insight or learning
- Third important insight or learning

**Code Sample** (if applicable):
```code-language
// Include a small, relevant code snippet if appropriate
```

**Tags:** #tag1 #tag2 #tag3
```

### Step 3: Update Topic README if Needed

If you're adding a new article to an existing topic/subtopic README, just add your article entry in chronological order (newest first).

If you're creating a new topic or subtopic:

1. Create a new directory for the topic/subtopic.
2. Create a README.md file in the new directory with:
   - Topic description
   - List of subtopics (if any)
   - List of articles (starting with yours)

### Step 4: Submit Your Contribution

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Add: [Article Title] to [Topic]"
   ```
2. Push to your fork:
   ```bash
   git push origin add/article-name
   ```
3. Create a pull request from your branch to the main repository.

## Pull Request Process

1. Use the provided PR template.
2. Complete all sections of the PR template.
3. Wait for a review from a maintainer.
4. Address any review comments if requested.

## Creating a New Topic

If your article doesn't fit into any existing topics:

1. Create a new directory under `/topics` with a descriptive, lowercase, hyphenated name.
2. Create a README.md file in the new directory with:
   ```markdown
   # Topic Name
   
   Brief description of what this topic covers and why it's valuable.
   
   ## Articles
   
   ### [Your Article Title](https://link-to-article)
   ...
   ```
3. Update the main README.md to include a link to your new topic.

## Style Guidelines

- Use clear, concise language in your summaries.
- Format code snippets with appropriate language tags.
- Include relevant tags to improve searchability.
- Be consistent with the established format.
- Keep summaries focused on the most valuable insights.

## Need Help?

If you're unsure about any part of the contribution process, please open an issue with your question, and a maintainer will assist you.

Thank you for sharing your knowledge with the team!