from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_drg_code_no_insurance():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterDrgCode": "439",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def encounter_record_drg_code_and_insurance():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterInsuredRank": "1",
        "encounterInsuredCategoryCode": "MC",
        "encounterInsuredCategorySystem": "urn:id:MEDICARE",
        "encounterInsuredCategoryText": "MEDICARE",
        "encounterDrgCode": "439",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_drg_code_no_insurance():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
        "extension": [
            {
                "valueString": "439",
                "url": "https://www.cms.gov/icd10m/version37-fullcode-cms/fullcode_cms/P0002.html"
            }
        ],
        "identifier": [
            {
                "id": "AN.hospa-ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "AN",
                            "display": "Account number"
                        }
                    ],
                    "text": "Account number"
                },
                "system": "urn:id:hospa",
                "value": "hospa_ENC1"
            },
            {
                "id": "VN.ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "VN",
                            "display": "Visit number"
                        }
                    ],
                    "text": "Visit number"
                },
                "system": "urn:id:hospa",
                "value": "ENC1"
            },
            {
                "id": "RI.hospa-ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "RI",
                            "display": "Resource identifier"
                        }
                    ],
                    "text": "Resource identifier"
                },
                "system": "urn:id:hospa",
                "value": "hospa_ENC1"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {
            "reference": "Patient/hospa-ENC1"
        }
    }


@pytest.fixture
def expected_encounter_drg_code_and_insured_extensions():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
        "extension": [
            {
                "id": "1",
                "extension": [
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-category",
                        "valueCodeableConcept": {
                            "coding": [{"system": "urn:id:MEDICARE", "code": "MC"}],
                            "text": "MEDICARE"
                        },
                    },
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-rank",
                        "valueInteger": 1
                    },
                ],
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured"
            },
            {
                "valueString": "439",
                "url": "https://www.cms.gov/icd10m/version37-fullcode-cms/fullcode_cms/P0002.html"
            },
        ],
        "identifier": [
            {
                "id": "AN.hospa-ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "AN",
                            "display": "Account number"
                        }
                    ],
                    "text": "Account number"
                },
                "system": "urn:id:hospa",
                "value": "hospa_ENC1"
            },
            {
                "id": "VN.ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "VN",
                            "display": "Visit number"
                        }
                    ],
                    "text": "Visit number"
                },
                "system": "urn:id:hospa",
                "value": "ENC1"
            },
            {
                "id": "RI.hospa-ENC1",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "RI",
                            "display": "Resource identifier"
                        }
                    ],
                    "text": "Resource identifier",
                },
                "system": "urn:id:hospa",
                "value": "hospa_ENC1"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {
            "reference": "Patient/hospa-ENC1"
        }
    }


def test_convert_record_encounter_drg_code_only_ext(
    encounter_record_drg_code_no_insurance, expected_encounter_drg_code_no_insurance
):
    group_by_key = encounter_record_drg_code_no_insurance.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_drg_code_no_insurance, None
    )

    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]
    assert result.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert len(result.identifier) == 3, "Encounter: identifier count is incorrect"

    expected_resource = Encounter(**expected_encounter_drg_code_no_insurance)
    fhir_result: Encounter = Encounter.parse_obj(result.dict())

    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}


# Insured only extension tested in test_encounter_insured_extension

# Test that both extensions are created compatibly in the same record
def test_convert_record_encounter_drg_code_and_insured_extensions(
    encounter_record_drg_code_and_insurance,
    expected_encounter_drg_code_and_insured_extensions
):
    group_by_key = encounter_record_drg_code_and_insurance.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_drg_code_and_insurance, None
    )

    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]
    assert result.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert len(result.identifier) == 3, "Encounter: identifier count is incorrect"
    expected_resource = Encounter(
        **expected_encounter_drg_code_and_insured_extensions
    )
    fhir_result: Encounter = Encounter.parse_obj(result.dict())

    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}
