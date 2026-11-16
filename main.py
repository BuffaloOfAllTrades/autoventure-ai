
import json
import re
import html
import time
import urllib.request
from datetime import datetime, timezone

API = "https://hacker-news.firebaseio.com/v0"

MAX_POSTS = 30
MAX_COMMENTS = 20


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AutoVentureAI/0.2"}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.load(res)


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def get_comments(post):
    comments = []

    for comment_id in post.get("kids", [])[:MAX_COMMENTS]:
        try:
            comment = get_json(
                f"{API}/item/{comment_id}.json"
            )

            if not comment or comment.get("deleted"):
                continue

            if comment.get("dead"):
                continue

            body = clean_text(comment.get("text", ""))

            if body:
                comments.append({
                    "text": body,
                    "author": comment.get("by", ""),
                    "id": comment_id
                })

        except Exception as e:
            print("Comment skipped:", e)

    return comments


def main():
    print("AutoVenture AI starting...")

    ids = get_json(API + "/askstories.json")
    results = []

    for item_id in ids[:MAX_POSTS]:
        try:
            post = get_json(
                f"{API}/item/{item_id}.json"
            )

            if not post:
                continue

            comments = get_comments(post)

            results.append({
                "id": item_id,
                "title": post.get("title", ""),
                "text": clean_text(
                    post.get("text", "")
                ),
                "url": (
                    "https://news.ycombinator.com/item?id="
                    + str(item_id)
                ),
                "score": post.get("score", 0),
                "comment_count": post.get("descendants", 0),
                "comments": comments
            })

            print(
                "Collected:",
                post.get("title", "")[:60],
                "| comments:",
                len(comments)
            )

            time.sleep(0.2)

        except Exception as e:
            print("Post skipped:", e)

    report = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_posts": len(results),
        "posts": results
    }

    with open(
        "report.json", "w", encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Collected", len(results), "posts")


if __name__ == "__main__":
    main()
