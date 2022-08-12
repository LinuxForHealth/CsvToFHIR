import json
import os
from typing import Dict

import numpy as np
import pytest
from pandas import DataFrame

from linuxforhealth.csvtofhir import converter
from linuxforhealth.csvtofhir.config import ConverterConfig
from linuxforhealth.csvtofhir.model.contract import DataContract
from linuxforhealth.csvtofhir.pipeline import tasks
from tests.support import resources_directory


@pytest.fixture
def data_contract_directory() -> str:
    return os.path.join(resources_directory, "data-contract")


@pytest.fixture
def data_contract_with_headers_data(data_contract_directory: str) -> Dict:
    """
    A dictionary data fixture containing DataContract compatible data which includes a headers definition.
    :return: dictionary
    """
    file_path = os.path.join(data_contract_directory, "data-contract-headers.json")
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def data_contract_with_headers_model(
    data_contract_with_headers_data: Dict,
) -> DataContract:
    """
    A DataContract model fixture, which is immutable.
    :param data_contract_with_headers_data: The input data
    :return: DataContract instance
    """
    return DataContract(**data_contract_with_headers_data)


@pytest.fixture
def data_contract_data(data_contract_directory: str) -> Dict:
    """
    A dictionary data fixture containing DataContract compatible data.
    :return: dictionary
    """
    file_path = os.path.join(data_contract_directory, "data-contract.json")
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def data_contract_model(data_contract_data: Dict) -> DataContract:
    """
    A DataContract model fixture, which is immutable.
    :param data_contract_data: The input data
    :return: DataContract instance
    """
    return DataContract(**data_contract_data)


@pytest.fixture
def data_contract_with_comments_data(data_contract_directory: str) -> Dict:
    """
    A dictionary data fixture containing DataContract compatible data with comments.
    :return: dictionary
    """
    file_path = os.path.join(data_contract_directory, "data-contract-comments.json")
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def data_contract_with_headers_comments_data(data_contract_directory: str) -> Dict:
    """
    A dictionary data fixture containing DataContract compatible data which includes a headers definition and comments.
    :return: dictionary
    """
    file_path = os.path.join(data_contract_directory, "data-contract-headers-comments.json")
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def csv_directory():
    return f"{resources_directory}/csv"


@pytest.fixture
def input_data_frame() -> DataFrame:
    """
    A DataFrame fixture used as an input to test cases.
    :return: DataFrame
    """
    data_frame: DataFrame = DataFrame()
    data_frame["hospitalId"] = ["hospa"]
    data_frame["encounterId"] = ["ENC1111"]
    data_frame["patientId"] = ["MRN1234"]
    data_frame["sex"] = ["M"]
    data_frame["dateOfBirth"] = ["1951-07-06"]
    data_frame["givenName"] = ["Thomas"]
    data_frame["familyName"] = ["Jones"]
    data_frame["ssn"] = ["123-45-6789"]
    data_frame["ssnSystem"] = ["http://hl7.org/fhir/sid/us-ssn"]
    data_frame["notNumber"] = [np.nan]
    data_frame["rowNum"] = [1]

    return data_frame


@pytest.fixture
def expected_data_frame(input_data_frame: DataFrame) -> DataFrame:
    """
    A DataFrame fixture used as an expected "output" and modified for test cases.
    The fixture is created using a deep copy of the input_data_frame fixture.
    :param input_data_frame: The source fixture
    :return:DataFrame
    """
    data: Dict = input_data_frame.to_dict(orient="series")
    data_frame: DataFrame = DataFrame.from_dict(data)
    return data_frame


@pytest.fixture
def monkeypatch_converter_config(monkeypatch):
    """
    Returns a function used to monkey patch the ConverterConfig.
    The function accepts a single parameter, the configuration directory.

    Example:

    def test_something(monkeypatch_converter_config):
         monkeypatch_converter_config(config_dir)
         assert 1 == 1

    :param monkeypatch: The pytest monkeypatch fixture
    :return: function
    """
    def _converter_config(config_dir: str = None):
        monkeypatch.setattr(converter,
                            "get_converter_config",
                            lambda: ConverterConfig(mapping_config_directory=config_dir)
                            )

        monkeypatch.setattr(tasks,
                            "get_converter_config",
                            lambda: ConverterConfig(mapping_config_directory=config_dir)
                            )
    return _converter_config
