from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_insurance():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterInsuredRank": "1",
        "encounterInsuredCategoryCode": "MC",
        "encounterInsuredCategorySystem": "urn:id:MEDICARE",
        "encounterInsuredCategoryText": "MEDICARE",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def encounter_record_insurance_entry_id():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterInsuredEntryId": "overwrite",
        "encounterInsuredRank": "1",
        "encounterInsuredCategoryCode": "MC",
        "encounterInsuredCategorySystem": "urn:id:MEDICARE",
        "encounterInsuredCategoryText": "MEDICARE",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def encounter_record_insurance_missing_rank():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterInsuredCategoryText": "MEDICARE",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_record_insurance_missing_rank():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
        "identifier": [
            {
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
                "value": "hospa_ENC1",
                "id": "AN.hospa-ENC1"
            },
            {
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
                "value": "hospa_ENC1",
                "id": "RI.hospa-ENC1"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-ENC1"},
        "extension": [
            {
                "id": "MEDICARE",
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured",
                "extension": [
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-category",
                        "valueCodeableConcept": {
                            "text": "MEDICARE"
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def expected_encounter_insured_only():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
        "identifier": [
            {
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
                "value": "hospa_ENC1",
                "id": "AN.hospa-ENC1"
            },
            {
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
                "value": "ENC1",
                "id": "VN.ENC1"
            },
            {
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
                "value": "hospa_ENC1",
                "id": "RI.hospa-ENC1"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-ENC1"},
        "extension": [
            {
                "id": 1,
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured",
                "extension": [
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-rank",
                        "valueInteger": 1
                    },
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-category",
                        "valueCodeableConcept": {
                            "coding": [{"system": "urn:id:MEDICARE", "code": "MC"}],
                            "text": "MEDICARE"
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def expected_encounter_insured_overwrite():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
        "identifier": [
            {
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
                "value": "hospa_ENC1",
                "id": "AN.hospa-ENC1"
            },
            {
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
                "value": "ENC1",
                "id": "VN.ENC1"
            },
            {
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
                "value": "hospa_ENC1",
                "id": "RI.hospa-ENC1"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-ENC1"},
        "extension": [
            {
                "id": "overwrite",
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured",
                "extension": [
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-rank",
                        "valueInteger": 1
                    },
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/insured-category",
                        "valueCodeableConcept": {
                            "coding": [{"system": "urn:id:MEDICARE", "code": "MC"}],
                            "text": "MEDICARE"
                        }
                    }
                ]
            }
        ]
    }


def test_convert_record_encounter_insured_ext(
    encounter_record_insurance, expected_encounter_insured_only
):
    group_by_key = encounter_record_insurance.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_insurance, None
    )

    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert len(result.identifier) == 3, "Encounter: identifier count is incorrect"

    expected_resource = Encounter(**expected_encounter_insured_only)
    fhir_result: Encounter = Encounter.parse_obj(result.dict())

    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}


def test_convert_record_encounter_insured_id_overwrite_ext(
    encounter_record_insurance_entry_id, expected_encounter_insured_overwrite
):
    group_by_key = encounter_record_insurance_entry_id.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_insurance_entry_id, None
    )

    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert len(result.identifier) == 3, "Encounter: identifier count is incorrect"
    expected_resource = Encounter(**expected_encounter_insured_overwrite)
    fhir_result: Encounter = Encounter.parse_obj(result.dict())

    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}


def test_convert_record_encounter_insurance_missing_rank(
    encounter_record_insurance_missing_rank,
    expected_encounter_record_insurance_missing_rank,
):
    group_by_key = encounter_record_insurance_missing_rank.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_insurance_missing_rank, None
    )

    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert len(result.identifier) == 2, "Encounter: identifier count is incorrect"
    expected_resource = Encounter(
        **expected_encounter_record_insurance_missing_rank
    )
    fhir_result: Encounter = Encounter.parse_obj(result.dict())

    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}
