
import json
import re
from datetime import datetime, timezone

SIGNALS = {
    "困りごと": [
        "problem", "issue", "struggle", "difficult",
        "frustrated", "annoying", "pain", "broken",
        "can't", "cannot", "hard to"
    ],
    "解決策の探索": [
        "how do", "how can", "looking for",
        "alternative", "recommend", "solution",
        "tool for", "is there", "anyone know"
    ],
    "支払い・購入意欲": [
        "pay for", "willing to pay", "pricing",
        "subscription", "expensive", "buy"
    ],
}

def analyze_post(post):
    title = post.get("title", "")
    text = title.lower()
    matched = {}

    for category, keywords in SIGNALS.items():
        hits = [
            word for word in keywords
            if word in text
        ]
        if hits:
            matched[category] = hits

    problem_hits = len(matched.get("困りごと", []))
    solution_hits = len(matched.get("解決策の探索", []))
    payment_hits = len(matched.get("支払い・購入意欲", []))

    score = min(
        100,
        problem_hits * 20
        + solution_hits * 15
        + payment_hits * 25
    )


    return {
        "title": title,
        "url": post.get("url", ""),
        "score": score,
        "signals": matched,
        
        "potential_opportunity": (
            score >= 30
            and (problem_hits > 0 or solution_hits > 0)
        )

    }

def main():
    with open("report.json", encoding="utf-8") as f:
        data = json.load(f)

    results = [
        analyze_post(post)
        for post in data.get("posts", [])
    ]
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    output = {
        "analyzed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_posts": len(results),
        "opportunities": [
            item for item in results
            if item["potential_opportunity"]
        ],
        "all_results": results
    }

    with open(
        "opportunities.json", "w", encoding="utf-8"
    ) as f:
        json.dump(
            output, f, ensure_ascii=False, indent=2
        )

    print(
        "Analysis complete:",
        len(output["opportunities"]),
        "potential opportunities"
    )

if __name__ == "__main__":
    main()
