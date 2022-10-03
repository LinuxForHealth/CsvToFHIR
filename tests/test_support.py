import json
import os
from typing import Dict, List

import pytest

from linuxforhealth.csvtofhir.support import (find_fhir_resources, is_valid_year, read_csv,

                                              validate_paths, parse_uri_scheme)


@pytest.fixture
def practitioner() -> str:
    data = {
        "id": "ABCDEF",
        "identifier": [
            {
                "id": "RI.ABCDEF",
                "system": "urn:id:hospb",
                "type": {
                    "coding": [
                        {
                            "code": "RI",
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203"
                        }
                    ],
                    "text": "Resource identifier"
                },
                "value": "ABCDEF"
            }
        ],
        "meta": {
            "extension": [
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/tenant-id",
                    "valueString": "sample-tenant"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-file-id",
                    "valueString": "testresults.csv"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-event-trigger",
                    "valueCodeableConcept": {
                        "text": "Observation"
                    }
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/process-timestamp",
                    "valueDateTime": "2022-03-28T13:35:48.720714+00:00"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-record-type",
                    "valueCodeableConcept": {
                        "text": "csv"
                    }
                }
            ]
        },
        "resourceType": "Practitioner"
    }
    return json.dumps(data)


@pytest.fixture
def observation() -> str:
    """
    :return: an Observation JSON FHIR resource
    """
    data = {
        "category": [
            {
                "coding": [
                    {
                        "code": "laboratory",
                        "display": "Laboratory",
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category"
                    }
                ],
                "text": "Laboratory"
            }
        ],
        "code": {
            "coding": [
                {
                    "code": "26499-4",
                    "system": "http://loinc.org"
                }
            ],
            "text": "#Neutrophils"
        },
        "effectiveDateTime": "2021-10-11T20:53:00+00:00",
        "encounter": {
            "reference": "Encounter/hospb-EZ100"
        },
        "id": "1648474548730029000.2fd8a5cb5f83411b81b29038d6ddcc0a",
        "identifier": [
            {
                "id": "AN.hospb-EZ100",
                "system": "urn:id:hospb",
                "type": {
                    "coding": [
                        {
                            "code": "AN",
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203"
                        }
                    ],
                    "text": "Account number"
                },
                "value": "hospb_EZ100"
            }
        ],
        "meta": {
            "extension": [
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/tenant-id",
                    "valueString": "sample-tenant"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-file-id",
                    "valueString": "testresults.csv"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-event-trigger",
                    "valueCodeableConcept": {
                        "text": "Observation"
                    }
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/process-timestamp",
                    "valueDateTime": "2022-03-28T13:35:48.720714+00:00"
                },
                {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/source-record-type",
                    "valueCodeableConcept": {
                        "text": "csv"
                    }
                }
            ]
        },
        "performer": [
            {
                "reference": "Practitioner/ABCDEF"
            }
        ],
        "referenceRange": [
            {
                "high": {
                    "unit": "thou/uL",
                    "value": 6.5
                },
                "low": {
                    "unit": "thou/uL",
                    "value": 1.4
                },
                "text": "1.40-6.50"
            }
        ],
        "resourceType": "Observation",
        "status": "final",
        "subject": {
            "reference": "Patient/hospb-EZ100"
        },
        "valueQuantity": {
            "unit": "thou/uL",
            "value": 7.9
        }
    }
    return json.dumps(data)


@pytest.fixture
def converter_results(practitioner, observation) -> List[str]:
    """
    csvtofhir.converter.convert result fixture containing a single patient result
    :return: List of results
    """
    return [practitioner, observation]


@pytest.mark.parametrize(
    "resource_type,is_match,resource_count",
    [("Practitioner", True, 1),
     ("practitioner", True, 1),
     ("Encounter", True, 0),
     ("Observation", False, 1),
     ("observation", False, 1)]
)
def test_find_fhir_resources(
    converter_results, resource_type: str, is_match: bool, resource_count: int
):
    """
    Validates find_fhir_resources to ensure the search is not case sensitive
    """

    actual_result: List[Dict] = find_fhir_resources(converter_results, resource_type)
    assert len(actual_result) == resource_count

    dictionary_results: List = list(
        filter(lambda x: isinstance(x, dict), actual_result)
    )
    assert len(actual_result) == len(dictionary_results)

    resource_types: List[str] = [
        d
        for d in dictionary_results
        if d.get("resourceType", "").lower() == resource_type.lower()
    ]
    assert len(resource_types) == len(actual_result)


def test_read_csv(data_contract_directory):
    """
    Tests the read_csv support function.

    :param data_contract_directory: The data contract directory fixture
    """
    filepath = os.path.join(data_contract_directory, "sex.csv")
    csv_dict = read_csv(filepath)
    assert csv_dict == {"default": "unknown", "M": "male", "F": "female", "O": "other"}


def test_is_valid_year():
    """
    Validates an input string is a valid year and within range of a patient event (e.g. birth, death)s
    """
    assert is_valid_year("1999")
    assert not is_valid_year("1880")
    assert not is_valid_year("2300")
    assert not is_valid_year("19991")
    assert not is_valid_year("1999abc")
    assert not is_valid_year("99")
    assert not is_valid_year("apple")


def test_validate_paths(data_contract_directory: str):
    """
    Validates positive and negative outcomes with validate_paths

    :param data_contract_directory: A path directory fixture used for a "valid" path
    """

    paths = [data_contract_directory]

    result: List[str] = validate_paths(paths, raise_exception=True)
    assert len(result) == 0

    result = validate_paths(paths, raise_exception=False)
    assert len(result) == 0

    paths.append("/tmp/bar/not-a-valid-path")
    result = validate_paths(paths, raise_exception=False)
    assert len(result) == 1

    with pytest.raises(FileNotFoundError):
        validate_paths(paths, raise_exception=True)


@pytest.mark.parametrize(
    "input_uri, expected_uri",
    [
        ("/opt/data/data.csv", "file"),
        ("C:/data/data.csv", "file"),
        ("http://someserver/file.dat", "http")
    ]
)
def test_parse_uri_scheme(input_uri, expected_uri):
    actual_scheme = parse_uri_scheme(input_uri)
    assert expected_uri == actual_scheme
