import json
import problem_json_formatter

def simplify_json(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    simplified_data = {
        "stat_status_pairs": []
    }

    for item in data['stat_status_pairs']:
        if not item['paid_only']:
            simplified_item = {
                "id": item['stat']['frontend_question_id'],
                "title": item['stat']['question__title'],
                "slug": item['stat']['question__title_slug'],
                "level": item['difficulty']['level']
            }
            simplified_data["stat_status_pairs"].append(simplified_item)

    with open(output_file, 'w') as file:
        json.dump(simplified_data, file, indent=4)

if __name__ == "__main__":
    # source url
    # https://leetcode.com/api/problems/all/

    input_file = 'raw.json'  # replace with the path to your input JSON file
    output_file = 'simplified_problems.json'  # replace with the desired output file path
    problem_json_formatter.format_json_file(input_file, silent=True)
    simplify_json(input_file, output_file)
