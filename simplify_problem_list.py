import json
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

import problem_json_formatter

RAW_FILE = Path('raw.json')
OUTPUT_FILE = Path('simplified_problems.json')
LEETCODE_API_URL = 'https://leetcode.com/api/problems/all/'


def fetch_json(url: str, output_path: Path) -> None:
    print(f"Fetching data from {url}...")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read()
    except HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code} while fetching {url}") from e
    except URLError as e:
        raise RuntimeError(f"Failed to reach {url}: {e.reason}") from e

    output_path.write_bytes(data)
    print(f"Saved raw data to {output_path}")


def simplify_json(input_path: Path, output_path: Path) -> None:
    print(f"Simplifying {input_path}...")
    data = json.loads(input_path.read_text(encoding='utf-8'))

    problems = [
        {
            "id": item.get('stat', {}).get('frontend_question_id'),
            "title": item.get('stat', {}).get('question__title'),
            "slug": item.get('stat', {}).get('question__title_slug'),
            "level": item.get('difficulty', {}).get('level'),
        }
        for item in data.get('stat_status_pairs', [])
        if not item.get('paid_only')
    ]

    output_path.write_text(
        json.dumps({"stat_status_pairs": problems}, indent=4),
        encoding='utf-8',
    )
    print(f"Saved {len(problems)} problems to {output_path}")


if __name__ == "__main__":
    fetch_json(LEETCODE_API_URL, RAW_FILE)
    print("Formatting raw JSON...")
    problem_json_formatter.format_json_file(RAW_FILE, silent=True)
    simplify_json(RAW_FILE, OUTPUT_FILE)
    print("Done!")
