import json


def save_result_to_json(data, filename):

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Results saved to {filename}")


def load_results_from_json(filename):

    with open(filename, 'r') as f:
        data = json.load(f)
    return data
