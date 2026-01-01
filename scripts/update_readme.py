#!/usr/bin/env python3
"""
scripts/update_readme.py

This script updates the repository README.md with a daily ledger entry.
Each row contains:
- date (ISO format)
- a short "thought" (from the Quotable API, with a local fallback)
- the top news headline (from TheNewsAPI, if configured)

Configuration:
- Set the environment variable THENEWS_API_KEY to enable news fetching.
"""

import os
import requests
from datetime import date

# Path to the README file that will be updated with a new row.
README_PATH = "README.md"

# External APIs used to fetch content for each ledger row.
QUOTABLE_URL = "https://api.quotable.io/random"
NEWS_URL = "https://api.thenewsapi.com/v1/news/top"

# API key read from the environment; if missing, news fetching is skipped.
NEWS_API_KEY = os.getenv("THENEWS_API_KEY")


def get_today():
    """
    Return today's date as an ISO-formatted string (YYYY-MM-DD).
    Separated into its own function to make testing easier.
    """
    return date.today().isoformat()


def get_thought():
    """
    Fetch a random quote from the Quotable API and return it in the format:
        "<content> — <author>"

    If the API request fails for any reason (network, rate limit, unexpected
    response), return a sensible fallback string.
    """
    try:
        response = requests.get(QUOTABLE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Compose the thought from the API response.
        return f"{data['content']} — {data['author']}"
    except Exception:
        # Use a short, local fallback thought if anything goes wrong.
        return "Pay attention to what compounds."


def get_top_news():
    """
    Fetch the top news headline using TheNewsAPI.

    Returns a single headline string on success. If the NEWS_API_KEY is not set
    or the API call fails / returns no articles, return a fallback message.

    Note: TheNewsAPI expects the api_token parameter named "api_token".
    """
    if not NEWS_API_KEY:
        # Early return if API key not configured.
        return "No news source configured."

    params = {
        "api_token": NEWS_API_KEY,
        "language": "en",
        "limit": 1, 
    }

    try:
        response = requests.get(NEWS_URL, params=params, timeout=10)
        response.raise_for_status()
        # The API returns articles under a "data" key; default to empty list.
        articles = response.json().get("data", [])
        if articles:
            # Return the title of the first/top article, stripped of extra whitespace.
            return articles[0]["title"].strip()
    except Exception:
        # Any failure falls through to the fallback message below.
        pass

    # Fallback when there are no articles or the request failed.
    return "World unusually quiet today."


def entry_exists(content, today):
    """
    Check whether an entry for the given date already exists in the README content.

    This does a simple substring check for a Markdown table row starting with
    the date value (e.g., "| 2026-01-01 |"). This assumes the README uses a
    similar table format for the daily ledger.
    """
    return f"| {today} |" in content


def append_row(content, row):
    """
    Append a new table row to the existing README content.

    Uses rstrip() to remove trailing whitespace/newlines then adds a single
    newline and the new row followed by another newline to ensure file ends
    with a newline.
    """
    return content.rstrip() + "\n" + row + "\n"


def main():
    """
    Main orchestration: gather the date, thought, and news, build a table row,
    and append it to README.md if a row for today does not already exist.
    """
    today = get_today()
    thought = get_thought()
    news = get_top_news()

    # Build the Markdown table row to add.
    new_row = f"| {today} | {thought} | {news} |"

    # Read the current README content.
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Avoid duplicate entries for the same day.
    if entry_exists(content, today):
        print("Entry already exists for today. Skipping.")
        return

    # Append the new row and write back the updated content.
    updated = append_row(content, new_row)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print("Daily ledger updated.")
    print(f"Added row: {new_row}")


if __name__ == "__main__":
    main()
