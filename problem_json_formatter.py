import json
import os


def format_json_file(filepath, silent=True):
    # Check if the file exists
    if not os.path.exists(filepath):
        print(f"No file found at {filepath}")
        return

    try:
        # Open and read the file
        with open(filepath, 'r') as file:
            data = file.read()

        # Try to parse the JSON data
        json_data = json.loads(data)

        # Check if the JSON data contains newlines, suggesting it is already formatted
        if '\n' in data:
            if not silent:
                print("JSON file is already formatted.")
        else:
            # It's a single-line JSON, let's format it
            with open(filepath, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Formatted the JSON file at {filepath}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    # Path to the JSON file
    json_file_path = 'raw.json'

    # Call the function with the path to the JSON file
    format_json_file(json_file_path, silent=False)
