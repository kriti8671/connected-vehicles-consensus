import json

def save_results_to_json(data, filename):
    """
    Save simulation results to a JSON file.

    Args:
    - data (dict): The data to save in JSON format.
    - filename (str): The name of the JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Results saved to {filename}")

def load_results_from_json(filename):
    """
    Load simulation results from a JSON file.

    Args:
    - filename (str): The name of the JSON file to read from.

    Returns:
    - dict: The loaded data from the JSON file.
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    return data
