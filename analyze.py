
import json
import re
from datetime import datetime, timezone

SIGNALS = {
    "problem": (
        ["struggle", "frustrat", "annoying",
         "pain point", "difficult", "problem with",
         "issue with", "cannot", "can't",
         "hard to", "waste time", "tedious", "broken"],
        12
    ),
    "solution_search": (
        ["looking for", "alternative to",
         "recommend a", "recommendation for",
         "is there a tool", "anyone know a",
         "how can i", "how do i",
         "need a tool", "wish there was"],
        10
    ),
    "payment": (
        ["willing to pay", "would pay",
         "pay for", "subscription", "pricing",
         "too expensive", "budget for",
         "purchased", "bought"],
        20
    ),
    "repeat": (
        ["every day", "every week", "constantly",
         "always have to", "repeatedly",
         "hours each", "manually"],
        8
    )
}

EXCLUDE = [
    "show hn:", "tell hn:", "launch hn:",
    "who is hiring", "who wants to be hired",
    "ppi rises", "stock market", "earnings report"
]

BUSINESS_CONTEXT = [
    "my workflow", "my files", "my schedule",
    "my budget", "my photos", "my email",
    "my tasks", "my documents", "my expenses",
    "my subscriptions"
]


def has_phrase(text, phrase):
    pattern = (
        r"(?<![a-z])"
        + re.escape(phrase)
        + r"(?![a-z])"
    )
    return re.search(pattern, text) is not None


def analyze_post(post):
    title = str(post.get("title") or "")
    body = str(
        post.get("text")
        or post.get("body")
        or post.get("selftext")
        or ""
    )

    text = (title + " " + body[:3000]).lower()
    matched = {}

    for category, (keywords, weight) in SIGNALS.items():
        hits = [
            word for word in keywords
            if has_phrase(text, word)
        ]
        if hits:
            matched[category] = hits

    excluded = any(
        title.lower().startswith(x)
        for x in EXCLUDE
    )

    score = sum(
        min(len(matched.get(category, [])), 2) * weight
        for category, (_, weight) in SIGNALS.items()
    )

    context_hits = [
        word for word in BUSINESS_CONTEXT
        if has_phrase(text, word)
    ]

    if context_hits:
        score += 10

    if not (
        matched.get("problem")
        or matched.get("solution_search")
    ):
        score = min(score, 25)

    if excluded:
        score = 0

    score = min(score, 100)

    return {
        "title": title,
        "url": post.get("url", ""),
        "score": score,
        "signals": matched,
        "context_signals": context_hits,
        "excluded": excluded,
        "potential_opportunity": (
            score >= 70
            and bool(
                matched.get("problem")
                or matched.get("solution_search")
            )
        ),
        "assessment": (
            "keyword-based lead; not validated demand"
        )
    }


def main():
    with open("report.json", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("posts", [])

    if not isinstance(posts, list):
        raise ValueError(
            "report.json posts must be a list"
        )

    results = [
        analyze_post(post)
        for post in posts
        if isinstance(post, dict)
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
        "all_results": results,
        "method": (
            "Rule-based screening; "
            "scores are not purchase probabilities"
        )
    }

    with open(
        "opportunities.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "Analysis complete:",
        len(output["opportunities"]),
        "potential opportunities"
    )


if __name__ == "__main__":
    main()
