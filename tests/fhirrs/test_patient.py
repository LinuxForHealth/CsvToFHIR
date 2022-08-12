from typing import Dict, List

import pytest
from deepdiff import DeepDiff
from fhir.resources.patient import Patient

from linuxforhealth.csvtofhir.fhirrs.patient import convert_record


@pytest.fixture
def source_patient_record() -> Dict:
    """The source patient record fixture"""
    return {
        "accountNumber": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "nameLast": "Jones",
        "nameFirstMiddle": "Alex C",
        "race": "2028-9",
        "gender": "male",
        "birthDate": "1951-07-06",
        "ssn": "123-45-6789",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "postalCode": "64328",
        "driversLicense": "S1234567890",
        "resourceType": "Patient",
        "filePath": "/home/csv/input.csv",
        # Purposely NO deceasedBoolean to confirm no boolean created
        "rowNum": 0
    }


@pytest.fixture
def patient_expected():
    expected = {
        "resourceType": "Patient",
        "id": "hospa-ENC1111",
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/local-race-cd",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-Race",
                            "display": "Asian",
                            "code": "2028-9"
                        }
                    ],
                    "text": "Asian"
                }
            }
        ],
        "identifier": [
            {
                "id": "AN.hospa-ENC1111",
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
                "value": "hospa_ENC1111"
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
            },
            {
                "id": "DL.S1234567890",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "DL",
                            "display": "Driver's license number"
                        }
                    ],
                    "text": "Driver's license number"
                },
                "value": "S1234567890"
            },
        ],
        "name": [
            {
                "text": "Alex C Jones",
                "family": "Jones",
                "given": ["Alex", "C"]
            }
        ],
        "gender": "male",
        "birthDate": "1951-07-06",
        "address": [
            {
                "postalCode": "64328"
            }
        ]
        # NO deceasedBoolean created
    }

    return expected


@pytest.fixture
def format_test_patient_record() -> Dict:
    """The source patient record fixture"""
    return {
        "patientInternalId": "1-Illegal.Char id_",
        "accountNumber": "hospa_ENC1111",
        "ssn": "000-00-0000",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "mrn": "MR-1111",
        "nameFirstMiddleLast": "Sara J Parker",
        "gender": "female",
        "birthDate": "2000",  # can be just the year
        "address1": "123 Main St",
        "address2": "Apt4A",
        "city": "New London",
        "state": "CT",
        "postalCode": "78099-0001",
        "telecomPhone": "555-555-5555",
        "race": "UNK",
        "raceSystem": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
        "raceText": "998",
        "ethnicity": "H",
        "ethnicitySystem": "urn:oid:2.16.840.1.113883.6.238",
        "ethnicityText": "613",
        "resourceType": "Patient",
        "deceasedBoolean": "False",
        "ageInWeeksForAgeUnder2Years": "69",
        "ageInMonthsForAgeUnder8Years": "17",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def format_test_patient_expected():
    expected = {
        "resourceType": "Patient",
        "id": "1-Illegal.Char-id-",
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/local-race-cd",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
                            "code": "UNK"
                        }
                    ],
                    "text": "998"
                }
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/ethnicity",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "urn:oid:2.16.840.1.113883.6.238",
                            "display": "Hispanic or Latino",
                            "code": "H"
                        }
                    ],
                    "text": "613"
                }
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/snapshot-age-in-months",
                "valueUnsignedInt": 17
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/snapshot-age-in-weeks",
                "valueUnsignedInt": 69
            }
        ],
        "identifier": [
            {
                "id": "PI.1-Illegal.Char-id-",
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
                "value": "1-Illegal.Char id_"
            },
            {
                "id": "MR.MR-1111",
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
                "value": "MR-1111"
            },
            {
                "id": "AN.hospa-ENC1111",
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
                "value": "hospa_ENC1111"
            }
        ],
        "name": [
            {
                "text": "Sara J Parker",
                "family": "Parker",
                "given": ["Sara", "J"]
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": "555-555-5555"
            }
        ],
        "gender": "female",
        "birthDate": "2000",
        "deceasedBoolean": False,
        "address": [
            {
                "line": ["123 Main St", "Apt4A"],
                "city": "New London",
                "state": "CT",
                "postalCode": "78099-0001"
            }
        ],
    }
    return expected


def test_convert_record(source_patient_record, patient_expected):
    group_by_key = source_patient_record["accountNumber"]

    patient_data: List[Dict] = convert_record(group_by_key, source_patient_record, None)

    assert len(patient_data) == 1
    patient = patient_data[0]
    # loading into fhir.resource test validity of the object
    fhir_patient: Patient = Patient.parse_obj(patient.dict())

    assert fhir_patient.resource_type == "Patient"
    assert fhir_patient.identifier
    assert len(fhir_patient.identifier) == 3  # Account Number, SSN and DL

    expected_resource = Patient(**patient_expected)
    diff = DeepDiff(expected_resource, fhir_patient, ignore_order=True)
    assert diff == {}


def test_patient_formatting_options(
    format_test_patient_record, format_test_patient_expected
):
    group_by_key = format_test_patient_record["accountNumber"]

    patient_data: List[Dict] = convert_record(
        group_by_key, format_test_patient_record, None
    )

    assert len(patient_data) == 1
    patient = patient_data[0]
    # loading into fhir.resource test validity of the object
    fhir_patient: Patient = Patient.parse_obj(patient.dict())

    assert fhir_patient.resource_type == "Patient"
    assert len(fhir_patient.identifier) == 3  # Account Number and PI

    expected_resource = Patient(**format_test_patient_expected)
    diff = DeepDiff(expected_resource, fhir_patient, ignore_order=True)
    assert diff == {}
