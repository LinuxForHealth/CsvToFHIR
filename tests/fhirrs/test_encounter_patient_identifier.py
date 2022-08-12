from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.patient import Patient
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_hospitalization_with_patient_id():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "patientInternalId": "hospa_PI12345",
        "mrn": "PI12345",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_patient_record_hospitalization_with_patient_id():
    return {
        "resourceType": "Patient",
        "id": "hospa-PI12345",
        "identifier": [
            {
                "id": "PI.hospa-PI12345",
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
                "value": "hospa_PI12345"
            },
            {
                "id": "MR.PI12345",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical record number"
                        }
                    ],
                    "text": "Medical record number"
                },
                "system": "urn:id:hospa",
                "value": "PI12345"
            },
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
            }
        ]
    }


@pytest.fixture
def expected_encounter_record_hospitalization_with_patient_id():
    return {
        "resourceType": "Encounter",
        "id": "hospa-ENC1",
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
            {
                "id": "PI.hospa-PI12345",
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
                "value": "hospa_PI12345"
            },
            {
                "id": "MR.PI12345",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical record number"
                        }
                    ],
                    "text": "Medical record number"
                },
                "system": "urn:id:hospa",
                "value": "PI12345"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-PI12345"}
    }


def test_convert_record_encounter_drg_code_only_ext(
        encounter_record_hospitalization_with_patient_id,
        expected_patient_record_hospitalization_with_patient_id,
        expected_encounter_record_hospitalization_with_patient_id):
    group_by_key = encounter_record_hospitalization_with_patient_id.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_hospitalization_with_patient_id, None
    )

    assert len(results) == 2, "Unexpected resource count generated"
    result_patient: Resource = results[0]
    result_encounter: Resource = results[1]
    assert result_patient.resource_type == "Patient", (
        "Unexpected Resource Type: " + result_patient.resource_type
    )
    assert result_encounter.resource_type == "Encounter", (
        "Unexpected Resource Type: " + result_encounter.resource_type
    )
    assert len(result_patient.identifier) == 3, "Patient: identifier count is incorrect"
    assert len(result_encounter.identifier) == 5, "Encounter: identifier count is incorrect"

    expected_resource = Patient(**expected_patient_record_hospitalization_with_patient_id)
    fhir_result: Patient = Patient.parse_obj(result_patient.dict())
    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}

    expected_resource = Encounter(**expected_encounter_record_hospitalization_with_patient_id)
    fhir_result: Encounter = Encounter.parse_obj(result_encounter.dict())
    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}
