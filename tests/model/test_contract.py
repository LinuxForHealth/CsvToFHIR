from typing import Dict

import pytest
import pydantic

from linuxforhealth.csvtofhir.model.contract import DataContract
from linuxforhealth.csvtofhir.config import ConverterConfig, get_converter_config
from linuxforhealth.csvtofhir.converter import load_data_contract


@pytest.mark.parametrize(
    "fixture_name", [
        "data_contract_data",
        "data_contract_with_comments_data",
        "data_contract_with_headers_comments_data",
        "data_contract_with_headers_data"
    ]
)
def test_valid_model(fixture_name, request):
    """
    Validates that a valid data contract does not raise an Exception.

    :param fixture_name: The name of the pytest fixture.
    :param request: Provides information on the executing test function
    """
    fixture: Dict = request.getfixturevalue(fixture_name)
    DataContract(**fixture)


def test_general_section_validations(data_contract_data: Dict):
    """
    Tests GeneralSection model validations
    :param data_contract_data: The input data dictionary
    """
    general_data = data_contract_data["general"]
    general_data["timeZone"] = "PEST"
    with pytest.raises(ValueError):
        DataContract(**data_contract_data)


def test_file_definition_resource_type(data_contract_data: Dict):
    """
    Tests FileDefinition.validate_resource_type
    :param data_contract_data: The input data dictionary
    """
    data_contract_data["fileDefinitions"]["Patient"]["resourceType"] = "Patientz"
    with pytest.raises(ValueError):
        DataContract(**data_contract_data)


def test_file_definition_task_invalid_name(data_contract_data: Dict):
    """
    Tests Task validations where a task name is invalid
    :param data_contract_data: The input data dictionary
    """
    tasks = data_contract_data["fileDefinitions"]["Patient"]["tasks"]
    tasks[0]["name"] = "invalid_task_name"

    with pytest.raises(ValueError) as exec_info:
        DataContract(**data_contract_data)

    assert "Unable to load task" in str(exec_info.value)


def test_file_definition_task_invalid_params_length(data_contract_data: Dict):
    """
    Tests Task validations where task parameters do not have the minimum number of parameters required by the function
    :param data_contract_data: The input data dictionary
    """
    tasks = data_contract_data["fileDefinitions"]["Patient"]["tasks"]
    tasks[0]["params"].clear()

    with pytest.raises(ValueError) as exec_info:
        DataContract(**data_contract_data)

    assert "Number of provided task params" in str(exec_info.value)


def test_file_definition_task_invalid_params_name(data_contract_data: Dict):
    """
    Tests Task validations where a task parameter name is invalid
    :param data_contract_data: The input data dictionary
    """
    tasks = data_contract_data["fileDefinitions"]["Patient"]["tasks"]
    name_value = tasks[0]["params"].pop("name")
    tasks[0]["params"]["invalid_parameter"] = name_value

    with pytest.raises(ValueError) as exec_info:
        DataContract(**data_contract_data)

    assert "Parameter invalid_parameter is not found in" in str(exec_info.value)


def test_file_definition_task_omit_default_parameter(data_contract_data: Dict):
    """
    Tests Task validations where a default parameter is not included in the task configuration.
    Expected result is that the configuration is valid.
    :param data_contract_data: The input data dictionary
    """
    tasks = data_contract_data["fileDefinitions"]["Patient"]["tasks"]
    # date_format has a default value validate it can be omitted
    del tasks[1]["params"]["date_format"]
    d: DataContract = DataContract(**data_contract_data)
    assert d is not None


def test_file_definition_task_no_required_args(data_contract_data: Dict):
    """
    Tests Task validations with a task config that has no required arguments
    Expected result is that the configuration is valid and does not raise a validation error.
    :param data_contract_data: The input data dictionary
    """
    tasks = data_contract_data["fileDefinitions"]["Patient"]["tasks"]
    # task with no required parameters
    tasks.append({"name": "set_nan_to_none"})
    d: DataContract = DataContract(**data_contract_data)
    assert d is not None

    # task with no required parameters - empty params dictionary
    tasks.append({"name": "set_nan_to_none", "params": {}})
    d: DataContract = DataContract(**data_contract_data)
    assert d is not None

    # task with no required parameters - params set to None
    tasks.append({"name": "set_nan_to_none", "params": None})
    d: DataContract = DataContract(**data_contract_data)
    assert d is not None


def test_datacontract_with_invalid_external_config(
    data_contract_directory: str,
    monkeypatch,
):
    """
    Test that loading an invalid external fileDefinition raises a validation error 
    at load time

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: pytest monkeypatch fixture
    """
    # bootstrap config
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    config: ConverterConfig = ConverterConfig(
        mapping_config_file_name="data-contract-fixed-width-external-invalid-config.json"
    )
    
    get_converter_config.cache_clear()
    with pytest.raises(pydantic.error_wrappers.ValidationError) as exec_info:
        contract: DataContract = load_data_contract(config.configuration_path)

    get_converter_config.cache_clear()


def test_datacontract_with_valid_external_config(
    data_contract_directory: str,
    monkeypatch,
):
    """
    Test that loading a valid external fileDefinition works as expected

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: pytest monkeypatch fixture
    """
    # bootstrap config
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    config: ConverterConfig = ConverterConfig(
        mapping_config_file_name="data-contract-fixed-width-external-config.json"
    )
    
    get_converter_config.cache_clear()
    
    contract: DataContract = load_data_contract(config.configuration_path)

    assert contract is not None
    assert isinstance(contract.fileDefinitions, Dict)

    get_converter_config.cache_clear()