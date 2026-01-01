import os
import requests
from datetime import date

README_PATH = "README.md"

QUOTABLE_URL = "https://api.quotable.io/random"
NEWS_URL = "https://api.thenewsapi.com/v1/news/top"
NEWS_API_KEY = os.getenv("THENEWS_API_KEY")


def get_today():
    return date.today().isoformat()


def get_thought():
    try:
        response = requests.get(QUOTABLE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{data['content']} — {data['author']}"
    except Exception:
        return "Pay attention to what compounds."


def get_top_news():
    if not NEWS_API_KEY:
        return "No news source configured."

    params = {
        "api_token": NEWS_API_KEY,
        "language": "en",
        "limit": 1,
    }

    try:
        response = requests.get(NEWS_URL, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("data", [])
        if articles:
            return articles[0]["title"].strip()
    except Exception:
        pass

    return "World unusually quiet today."


def entry_exists(content, today):
    return f"| {today} |" in content


def append_row(content, row):
    return content.rstrip() + "\n" + row + "\n"


def main():
    today = get_today()
    thought = get_thought()
    news = get_top_news()

    new_row = f"| {today} | {thought} | {news} |"

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if entry_exists(content, today):
        print("Entry already exists for today. Skipping.")
        return

    updated = append_row(content, new_row)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print("Daily ledger updated.")


if __name__ == "__main__":
    main()
