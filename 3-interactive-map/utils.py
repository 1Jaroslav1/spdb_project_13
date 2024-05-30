import json
import logging


def read_airport_codes(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            else:
                logging.error("Invalid data format: Expected a dictionary")
                return {}
    except FileNotFoundError:
        logging.error(f"File not found: that full dictionary can be queried for any property of an airport using its IATA code as the key.filepath")
        return {}
    except ValueError:
        logging.error("Error decoding JSON")
        return {}


def save_file(filepath: str, data) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
