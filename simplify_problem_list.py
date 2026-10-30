"""Fetch public LeetCode problem metadata and preserve the existing JSON format."""

import json
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

RAW_FILE = Path("raw.json")
OUTPUT_FILE = Path("simplified_problems.json")
GRAPHQL_URL = "https://leetcode.com/graphql"
PAGE_SIZE = 100
MIN_FREE_PROBLEMS = 3000  # Safety check: last successful run had 3308.

QUERY = """
query problemsetQuestionListV2($skip: Int, $limit: Int, $categorySlug: String) {
  problemsetQuestionListV2(skip: $skip, limit: $limit, categorySlug: $categorySlug) {
    questions { questionFrontendId title titleSlug difficulty paidOnly }
    totalLength
    hasMore
  }
}
"""


def fetch_page(skip: int) -> dict:
    body = json.dumps({
        "operationName": "problemsetQuestionListV2",
        "query": QUERY,
        "variables": {
            "skip": skip,
            "limit": PAGE_SIZE,
            "categorySlug": "all-code-essentials",
        },
    }).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "leetcode-problems-updater/1.0",
            "Referer": "https://leetcode.com/problemset/",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        preview = error.read(350).decode("utf-8", errors="replace")
        raise RuntimeError(
            f"LeetCode GraphQL returned HTTP {error.code}. "
            f"Response preview: {preview!r}. "
            "A 403 may mean GitHub-hosted traffic is blocked; "
            "switching endpoints is not guaranteed to resolve that."
        ) from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"Cannot reach LeetCode GraphQL: {error}") from error

    if payload.get("errors"):
        raise RuntimeError(f"LeetCode GraphQL errors: {payload['errors']}")
    result = (payload.get("data") or {}).get("problemsetQuestionListV2")
    if not isinstance(result, dict) or not isinstance(result.get("questions"), list):
        raise RuntimeError(f"Unexpected LeetCode response at offset {skip}")
    return result


def fetch_all() -> list[dict]:
    questions = []
    skip = 0
    while True:
        page = fetch_page(skip)
        batch = page["questions"]
        if not batch:
            if page.get("hasMore"):
                raise RuntimeError(f"Empty page with hasMore=true at offset {skip}")
            break
        questions.extend(batch)
        total = page.get("totalLength")
        print(f"Fetched {len(questions)} / {total} problems", flush=True)
        if not page.get("hasMore"):
            if isinstance(total, int) and len(questions) != total:
                raise RuntimeError(f"Incomplete dataset: {len(questions)} of {total}")
            break
        skip += len(batch)
        time.sleep(0.5)
    return questions


def simplify(questions: list[dict]) -> list[dict]:
    difficulty = {"EASY": 1, "MEDIUM": 2, "HARD": 3}
    result = []
    for item in questions:
        if item["paidOnly"]:
            continue
        question_id = item["questionFrontendId"]
        if not question_id or not item.get("title") or not item.get("titleSlug"):
            raise RuntimeError(f"Missing required question fields: {item}")
        level = difficulty.get(item.get("difficulty"))
        if level is None:
            raise RuntimeError(f"Unknown difficulty: {item.get('difficulty')}")
        result.append({
            "id": int(question_id) if str(question_id).isdigit() else question_id,
            "title": item["title"],
            "slug": item["titleSlug"],
            "level": level,
        })
    if len(result) < MIN_FREE_PROBLEMS:
        raise RuntimeError(
            f"Only {len(result)} free problems returned; refusing to overwrite "
            f"{OUTPUT_FILE} (expected at least {MIN_FREE_PROBLEMS})."
        )
    return result


def main() -> None:
    print(f"Fetching public problem data from {GRAPHQL_URL} ...", flush=True)
    questions = fetch_all()
    simplified = simplify(questions)
    # Write only after all pages have been fetched and verified.
    RAW_FILE.write_text(json.dumps({"questions": questions}, indent=2), encoding="utf-8")
    OUTPUT_FILE.write_text(
        json.dumps({"stat_status_pairs": simplified}, indent=4), encoding="utf-8"
    )
    print(f"Saved {len(simplified)} free problems to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
