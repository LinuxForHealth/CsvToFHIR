import csv
import json
import logging
import os
from logging import NullHandler
from typing import Dict, List


def find_fhir_resources(resources: List, resource_type: str) -> List[Dict]:
    """
    Returns matching resources from a list
    :param resources: List of resources
    :param resource_type:
    :return: List of matching resources as Dictionaries
    """
    matches = []
    for result in resources:
        resource = json.loads(result)
        if resource.get("resourceType", "").lower() == resource_type.lower():
            matches.append(resource)

    return matches


def read_csv(filepath: str) -> Dict:
    """
    Reads a csv file and converts to Dict
    :param filepath: The csv file.
    :return: All the csv entries as Dict
    """
    csv_dict = {}

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_value = row["target_value"]
            csv_dict[row["source_value"]] = (
                target_value if target_value and target_value != "null" else None
            )

    return csv_dict


def get_logger(name):
    """
    Gets the logger
    :param name: A str with the name of the logger
    :return: Returns the logger object
    """
    logger = logging.getLogger(name)
    logger.addHandler(NullHandler())

    # uncomment the lines below to enable local environment logging

    # from logging import StreamHandler
    # logger.setLevel(logging.DEBUG)
    # stream_handler = StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)
    #
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)
    return logger


def is_valid_year(year: str) -> bool:
    """
    Is the input string a valid patient event year. 1900 <= year <= 2200.
    :param name: A patient event year. Must be 4 digits.
    :return: True if 1900 <= year <= 2200, otherwise False
    """
    try:
        int_year = int(year)
        return 1900 <= int_year and int_year <= 2200
    except (TypeError, ValueError):
        return False


def validate_paths(paths: List[str], raise_exception=True) -> List[str]:
    """
    Returns invalid file or directory paths from an input list, optionally raising an exception

    :param paths: The paths to validate
    :param raise_exception: If set to True, raises an exception if paths contains one ore more invalid paths.
    :return: List of invalid paths, if found and raise_exception is False
    """
    invalid_paths = [p for p in paths if not os.path.exists(p)]

    if invalid_paths and raise_exception:
        msg = "File paths not found"
        for p in invalid_paths:
            msg += f"\n {p}"
        raise FileNotFoundError(msg)

    return invalid_paths
