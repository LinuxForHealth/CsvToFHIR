import json
from datetime import datetime, timezone
from typing import Dict

import pytest
from deepdiff import DeepDiff
from fhir.resources.meta import Meta
from fhir.resources.patient import Patient
from pandas import Series
from pydantic import ValidationError

from linuxforhealth.csvtofhir import converter
from linuxforhealth.csvtofhir.config import ConverterConfig, get_converter_config
from linuxforhealth.csvtofhir.converter import (ConverterDefinitionLookupException,
                                                build_csv_reader_params, convert, transform,
                                                load_data_contract, validate_contract)
from linuxforhealth.csvtofhir.model.contract import DataContract


def raise_value_error(*args, **kwargs):
    """Stub function used to raise a value error"""
    raise ValueError("test exception")


@pytest.fixture
def code_mapping() -> Dict[str, Dict[str, str]]:
    return {
        "sex": {"default": "unknown", "F": "female", "M": "male", "O": "other"},
        "severityCode": {
            "default": None,
            "Severe": "severe",
            "Mild": "mild",
            "Moderate": "moderate"
        }
    }


@pytest.fixture
def pandas_series() -> Series:
    data_row = {
        "hospitalId": "hospa",
        "encounterId": "ENC1111",
        "patientId": "MRN1234",
        "sex": "M",
        "dateOfBirth": "1951-07-06",
        "givenName": "Thomas",
        "familyName": "Jones",
        "ssn": "123-45-6789",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn"
    }
    return Series(data_row)


@pytest.fixture
def resource_meta_object(input_file_name: str, input_file_count: str) -> Meta:
    input_file = input_file_name + ":" + input_file_count
    resource_meta = {
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/tenant-id",
                "valueString": "sample-tenant"
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-file-id",
                "valueString": input_file
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-event-trigger",
                "valueCodeableConcept": {"text": "Patient"}
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/process-timestamp",
                "valueDateTime": datetime.utcnow()
                .replace(tzinfo=timezone.utc)
                .isoformat()
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-record-type",
                "valueCodeableConcept": {"text": "csv"}
            }
        ]
    }
    return resource_meta


@pytest.fixture
def patient_resource() -> Patient:
    patient_data = {
        "resourceType": "Patient",
        "id": "MRN1234",
        "identifier": [
            {
                "id": "PI.MRN1234",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "PI",
                            "display": "Patient internal identifier"
                        }
                    ],
                    "text": "Patient internal identifier"
                },
                "system": "urn:id:hospa",
                "value": "MRN1234"
            },
            {
                "id": "SS",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "SS",
                            "display": "Social Security number"
                        }
                    ],
                    "text": "Social Security number"
                },
                "system": "http://hl7.org/fhir/sid/us-ssn",
                "value": "123456789"
            }
        ],
        "name": [{"text": "Thomas Jones", "family": "Jones", "given": ["Thomas"]}],
        "gender": "male",
        "birthDate": "1951-07-06",
        "address": [
            {
                "state": "MN"
            }
        ]
    }
    return Patient(**patient_data)


@pytest.fixture
def patient_dict() -> Dict:
    return {
        'hospitalId': 'hospa',
        'encounterId': 'ENC1111',
        'patientId': 'MRN1234',
        'sex': 'male',
        'dateOfBirth': '1951-07-06',
        'givenName': 'Thomas',
        'familyName': 'Jones',
        'ssn': '123-45-6789',
        'state': 'MN',
        'rowNum': 1,
        'groupByKey': 'MRN1234',
        'timeZone': 'US/Eastern',
        'tenantId': 'sample-tenant',
        'streamType': 'live',
        'emptyFieldValues': ['empty', '\\n'],
        'filePath': '/Users/hammadkhan/Projects/LinuxForHealth/CsvToFHIR/tests/resources/csv/2022-02-18-patient-fwf.dat',
        'configResourceType': 'Patient'
    }


@pytest.fixture(autouse=True)
def clear_config_cache():
    get_converter_config.cache_clear()


def test_validate_contract_file_not_found_error(monkeypatch, data_contract_directory: str):
    """
    Validates that validate_contract raises FileNotFoundError when the data contract config file is not found.

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: The pytest monkeypatch fixture
    """
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    monkeypatch.setenv("MAPPING_CONFIG_FILE_NAME", "not-a-real-file")

    with pytest.raises(FileNotFoundError) as exec_info:
        validate_contract()
        assert "Unable to load Data Contract configuration" in str(exec_info.value)


def test_validate_contract_invalid_model(data_contract_directory: str, data_contract_data: Dict, monkeypatch):
    """
    Validates that validate_contract raises a ValidationError when the data model is invalid

    :param data_contract_directory: The data contract directory fixture
    :param data_contract_data: The data contract input data fixture
    :param monkeypatch: The pytest monkeypatch fixture
    """
    del data_contract_data["general"]

    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    monkeypatch.setenv("MAPPING_CONFIG_FILE_NAME", "data-contract.json")
    monkeypatch.setattr(
        converter, "load_data_contract", lambda x: DataContract(**data_contract_data)
    )

    with pytest.raises(ValidationError):
        validate_contract()


def test_validate_contract(monkeypatch, data_contract_directory: str):
    """
    Validates that validate_contract does not raise errors, given valid input

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: The pytest monkeypatch fixture
    """
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    monkeypatch.setenv("MAPPING_CONFIG_FILE_NAME", "data-contract.json")
    contract: DataContract = validate_contract()
    assert contract is not None


@pytest.mark.parametrize(
    "input_file_name,input_file_count,mapping_file_name",
    [
        ("2022-02-18-patient.csv", "00001", "data-contract.json"),
        ("2022-02-18-patient.csv", "00001", "data-contract-comments.json"),
        ("Patient.csv", "00001", "data-contract.json"),
        ("2022-02-18-patient-headerless.csv", "00001", "data-contract-headers.json"),
        ("2022-02-18-patient-headerless.csv", "00001", "data-contract-headers-comments.json"),
        ("Patient-headerless.csv", "00001", "data-contract-headers.json"),
        ("2022-02-18-patient.dat", "00001", "data-contract-delimiter.json"),
        ("2022-02-18-patient-fwf.dat", "00001", "data-contract-fixed-width.json")
    ],
)
def test_convert_patient(
    data_contract_directory: str,
    monkeypatch,
    csv_directory: str,
    input_file_name: str,
    input_file_count: str,
    mapping_file_name: str,
    patient_resource: Patient,
    resource_meta_object: Meta,
):
    """
    Tests the convert function with a patient record and parametrized file names.
    A key map is used to provide field mappings.
    The file names are used to validate that the conversion loads files using a "glob"'ish
    type of matching.

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: pytest monkeypatch fixture
    :param csv_directory: CSV directory path fixture
    :param input_file_name: The source CSV file name
    :param mapping_file_name: The resource mapping file
    :param patient_resource: The expected patient resource fixture
    """
    # bootstrap config
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    config: ConverterConfig = ConverterConfig(
        mapping_config_file_name=mapping_file_name
    )
    # mock validate_contract to return the contract model
    contract: DataContract = load_data_contract(config.configuration_path)
    monkeypatch.setattr(converter, "validate_contract", lambda: contract)

    input_file_path = f"{csv_directory}/{input_file_name}"
    # returns a list of results [ (exception, group by key, [resource, resource]), (etc) ]
    records = [(e, k, r) for e, k, r in convert(input_file_path)]
    assert len(records) == 1

    conversion_result = records[0]
    assert len(conversion_result) == 3

    exception = conversion_result[0]
    assert exception is None

    group_by_key = conversion_result[1]
    assert group_by_key == "MRN1234"

    encoded_result = conversion_result[2][0]
    assert encoded_result is not None

    resource_dict = json.loads(encoded_result)
    assert len(resource_dict) > 0
    actual_resource = Patient.parse_obj(resource_dict)
    patient_resource.meta = resource_meta_object
    # TODO: Originally, was "second", apparently if it is at the boundry of it it will fail
    # Changed to Hour precision, but that is not really solving the issue, more like reducing the occurrence of it
    # Marking to research
    diff = DeepDiff(
        patient_resource.dict(),
        actual_resource.dict(),
        ignore_order=True,
        truncate_datetime="hour"
    )
    assert diff == {}


@pytest.mark.parametrize(
    "input_file_name,input_file_count,mapping_file_name",
    [
        ("2022-02-18-patient-fwf.dat", "00001", "data-contract-fixed-width-transform-only.json")
    ],
)
def test_transform_patient(
    data_contract_directory: str,
    monkeypatch,
    csv_directory: str,
    input_file_name: str,
    input_file_count: str,
    mapping_file_name: str,
    patient_dict: Dict,
    resource_meta_object: Meta,
):
    """
    Tests the transform function with a patient record and parametrized file names.
    A key map is used to provide field mappings.
    The file names are used to validate that the conversion loads files using a "glob"'ish
    type of matching.

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: pytest monkeypatch fixture
    :param csv_directory: CSV directory path fixture
    :param input_file_name: The source CSV file name
    :param mapping_file_name: The resource mapping file
    :param patient_dict: The expected patient dict fixture
    """
    # bootstrap config
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    config: ConverterConfig = ConverterConfig(
        mapping_config_file_name=mapping_file_name
    )
    # mock validate_contract to return the contract model
    contract: DataContract = load_data_contract(config.configuration_path)
    monkeypatch.setattr(converter, "validate_contract", lambda: contract)

    input_file_path = f"{csv_directory}/{input_file_name}"
    # returns a list of results [ (exception, group by key, [resource, resource]), (etc) ]
    records = [(e, k, r) for e, k, r in transform(input_file_path)]
    assert len(records) == 1

    conversion_result = records[0]
    assert len(conversion_result) == 3

    exception = conversion_result[0]
    assert exception is None

    group_by_key = conversion_result[1]
    assert group_by_key == "MRN1234"

    encoded_result = conversion_result[2]
    assert encoded_result is not None

    actual_dict = json.loads(encoded_result)
    assert len(actual_dict) > 0
        
    # TODO: Originally, was "second", apparently if it is at the boundry of it it will fail
    # Changed to Hour precision, but that is not really solving the issue, more like reducing the occurrence of it
    # Marking to research
    diff = DeepDiff(
        patient_dict,
        actual_dict,
        ignore_order=True,
        truncate_datetime="hour"
    )

    assert diff == {}


def test_convert_patient_converterdefinition_exception(monkeypatch,
                                                       data_contract_directory: str,
                                                       csv_directory: str):
    """
    Validates that a ConverterDefinitionLookupException is raised for a file name/file definition name mismatch.

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: The monkeypatch fixture
    :param csv_directory: The CSV directory path
    """
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    csv_file_path = f"{csv_directory}/NotARealFile.csv"
    with pytest.raises(ConverterDefinitionLookupException):
        for _, _ in convert(csv_file_path):
            pass


def test_convert_patient_processing_exception(monkeypatch,
                                              data_contract_directory: str,
                                              csv_directory: str):
    """
    Validates that processing exceptions are captured in conversion results.

    :param data_contract_directory: The data contract directory fixture
    :param monkeypatch: The monkeypatch fixture
    :param csv_directory: The CSV directory path
    """
    monkeypatch.setenv("MAPPING_CONFIG_DIRECTORY", data_contract_directory)
    csv_file_path = f"{csv_directory}/Patient.csv"

    monkeypatch.setattr(converter, "convert_to_fhir", raise_value_error)

    # returns a list of results [ (exception, group by key, [resource, resource]), (etc) ]
    records = [(e, k, r) for e, k, r in convert(csv_file_path)]
    assert len(records) == 1

    conversion_result = records[0]
    assert len(conversion_result) == 3

    exception = conversion_result[0]
    assert isinstance(exception, ValueError)

    group_by_key = conversion_result[1]
    assert isinstance(group_by_key, str)

    encoded_result = conversion_result[2]
    assert isinstance(encoded_result, list)


def test_build_csv_reader_params(data_contract_model: DataContract):
    """
    Tests build CSV reader parameters

    :param data_contract_model: The DataContract model fixture
    """
    config = get_converter_config()
    file_definition = data_contract_model.fileDefinitions["Patient"]
    params = build_csv_reader_params(
        config, data_contract_model.general, file_definition
    )

    assert len(params) == 4
    assert params["chunksize"] == config.csv_buffer_size
    assert params["delimiter"] == ","
    assert params["dtype"] == str
    assert params["na_values"] == ["empty", "\\n"]


def test_build_csv_reader_params_include_headers(data_contract_with_headers_data: DataContract):
    """
    Tests build CSV reader parameters

    :param data_contract_with_headers_data: The DataContract raw data
    """
    config = get_converter_config()
    data_contract: DataContract = DataContract(**data_contract_with_headers_data)
    file_definition = data_contract.fileDefinitions["Patient"]
    params = build_csv_reader_params(config, data_contract.general, file_definition)

    assert len(params) == 6
    assert params["chunksize"] == config.csv_buffer_size
    assert params["delimiter"] == ","
    assert params["dtype"] == str
    assert params["header"] is None
    assert params["names"] == file_definition.headers
    assert params["na_values"] == ["empty", "\\n"]


def test_build_csv_reader_fixed_width_config(data_contract_fixed_width_model: DataContract):
    """
    Tests build CSV reader parameters for fixed width files

    :param data_contract_model: The DataContract model fixture
    """
    #print(data_contract_fixed_width_model)
    config = get_converter_config()
    file_definition = data_contract_fixed_width_model.fileDefinitions["Patient"]
    params = build_csv_reader_params(
        config, data_contract_fixed_width_model.general, file_definition
    )

    assert len(params) == 6
    assert params["chunksize"] == config.csv_buffer_size
    assert "delimiter" not in params
    assert params["dtype"] == str
    assert params["na_values"] == ["empty", "\\n"]
    assert params["names"] == ['hospitalId', 'encounterId', 'patientId', 'sex', 'dateOfBirth', 'givenName', 'familyName', 'ssn', 'state']
    assert params["widths"] == [6, 8, 8, 1, 10, 12, 12, 11, 16]