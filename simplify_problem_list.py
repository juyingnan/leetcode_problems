import json
import urllib.request
from urllib.error import URLError, HTTPError

import problem_json_formatter

RAW_FILE = 'raw.json'
OUTPUT_FILE = 'simplified_problems.json'
LEETCODE_API_URL = 'https://leetcode.com/api/problems/all/'


def fetch_json(url: str, output_file: str) -> None:
    print(f"Fetching data from {url}...")
    # Use urllib to avoid extra dependencies.
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read()
    except HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code} while fetching {url}") from e
    except URLError as e:
        raise RuntimeError(f"Failed to reach {url}: {e.reason}") from e

    with open(output_file, 'wb') as file:
        file.write(data)
    print(f"Saved raw data to {output_file}")


def simplify_json(input_file: str, output_file: str) -> None:
    print(f"Simplifying {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    simplified_data = {
        "stat_status_pairs": [
            {
                "id": item.get('stat', {}).get('frontend_question_id'),
                "title": item.get('stat', {}).get('question__title'),
                "slug": item.get('stat', {}).get('question__title_slug'),
                "level": item.get('difficulty', {}).get('level')
            }
            for item in data.get('stat_status_pairs', [])
            if not item.get('paid_only')
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(simplified_data, file, indent=4)
    print(f"Saved {len(simplified_data['stat_status_pairs'])} problems to {output_file}")

if __name__ == "__main__":
    fetch_json(LEETCODE_API_URL, RAW_FILE)
    print("Formatting raw JSON...")
    problem_json_formatter.format_json_file(RAW_FILE, silent=True)
    simplify_json(RAW_FILE, OUTPUT_FILE)
    print("Done!")
