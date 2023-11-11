import json

def load_credentials(file_path: str) -> dict:
    """Load credentials from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)