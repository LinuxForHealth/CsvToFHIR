import json
import os
import pprint

from pydantic import ValidationError

from linuxforhealth.csvtofhir.model.contract import DataContract


def validate_data_contract(args):
    """
    Validates a CSVToFHIR DataContract
    Command line arguments include:
    - "f": for the data contract file path
    :param args: parsed command line arguments
    """
    file_path: str = args.f
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"data contract file {file_path} not found"
        )

    with open(file_path, "rt", encoding="utf-8") as r:
        resource_data = json.load(r)

    contract: DataContract
    try:
        contract = DataContract(**resource_data)
    except ValidationError as validation_ex:
        print(f"Resource Mapping is invalid {validation_ex}")
    except Exception as general_ex:
        print(
            f"An exception occurred while attempting to validate resource mapping {general_ex}"
        )
    else:
        pprint.pprint(contract.dict(), indent=2)
        print("DataContract is valid")
