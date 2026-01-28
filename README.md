# leetcode_problems

A tool that fetches and simplifies LeetCode problem data.

## Features

- Fetches all LeetCode problems from the API
- Filters out paid-only problems
- Outputs a simplified JSON with problem id, title, slug, and difficulty level
- Auto-updates daily via GitHub Actions

## Files

- `simplified_problems.json` - Simplified problem list (free problems only)
- `raw.json` - Raw API response from LeetCode
- `simplify_problem_list.py` - Main script to fetch and process data

## Usage

```bash
python simplify_problem_list.py
```

## URL

https://leetcode.com/problems/