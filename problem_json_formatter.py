import json
from pathlib import Path


def format_json_file(filepath, silent=True):
    path = Path(filepath)

    if not path.exists():
        print(f"No file found at {filepath}")
        return

    try:
        data = path.read_text()
        json_data = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except OSError as e:
        print(f"Error reading file: {e}")
        return

    if '\n' in data:
        if not silent:
            print("JSON file is already formatted.")
        return

    path.write_text(json.dumps(json_data, indent=4))
    print(f"Formatted the JSON file at {filepath}")


if __name__ == '__main__':
    format_json_file('raw.json', silent=False)
