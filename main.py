
import json
import urllib.request
from datetime import datetime, timezone

API = "https://hacker-news.firebaseio.com/v0"

def get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AutoVentureAI/0.1"}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.load(res)

def main():
    print("AutoVenture AI starting...")

    ids = get_json(API + "/askstories.json")
    results = []

    for item_id in ids[:30]:
        try:
            post = get_json(
                f"{API}/item/{item_id}.json"
            )
            if not post:
                continue

            results.append({
                "title": post.get("title", ""),
                "url": "https://news.ycombinator.com/item?id="
                       + str(item_id),
                "score": post.get("score", 0)
            })
        except Exception as e:
            print("Skipped:", e)

    report = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "posts": results
    }

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(
            report, f,
            ensure_ascii=False,
            indent=2
        )

    print("Collected", len(results), "posts")

if __name__ == "__main__":
    main()
