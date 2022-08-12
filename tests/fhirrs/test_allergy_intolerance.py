import pytest

from typing import List
from deepdiff import DeepDiff
from fhir.resources.allergyintolerance import AllergyIntolerance

from linuxforhealth.csvtofhir.fhirrs.allergy_intolerance import convert_record


@pytest.fixture
def allergy_intolerance_basic():
    return {
        "assigningAuthority": "abc.abc",
        "accountNumber": "abc.abc_3465848537",
        "encounterInternalId": "abc.abc_3465848537",
        "encounterNumber": "3465848537",
        "allergyCodeText": "Statins-Hmg-Coa Reductase Inhibitor (Statins)",
        # Purposely no clinicalStatus or verificationStatus to confirm default is created
        # Test a ManifestationCode LIST with this data
        "allergyManifestationCodeList": ["1806006^^SNOMED", "271807003^^SNOMED"],
        "allergyCriticality": "high",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


# Expected out for basic test.
@pytest.fixture
def expected_allergy_intolerance_basic():
    return {
        "resourceType": "AllergyIntolerance",
        "id": "71a08158-a495-11ec-9a69-acde48001122",
        "identifier": [
            {
                "id": "AN.abc.abc-3465848537",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "AN",
                            "display": "Account number"
                        }
                    ],
                    "text": "Account number",
                },
                "system": "urn:id:abc.abc",
                "value": "abc.abc_3465848537",
            },
            {
                "id": "VN.3465848537",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "VN",
                            "display": "Visit number"
                        }
                    ],
                    "text": "Visit number",
                },
                "system": "urn:id:abc.abc",
                "value": "3465848537",
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "Statins-Hmg-Coa Reductase Inhibitor (Statins)"
            },
        ],
        "code": {"text": "Statins-Hmg-Coa Reductase Inhibitor (Statins)"},
        "patient": {"reference": "Patient/abc.abc-3465848537"},
        "encounter": {"reference": "Encounter/abc.abc-3465848537"},
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": "active",
                    "display": "Active"
                }
            ],
            "text": "Active",
        },
        "criticality": "high",
        "reaction": [
            {
                "manifestation": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "1806006"
                            }
                        ]
                    },
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "271807003"
                            }
                        ]
                    }
                ]
            }]
    }


# A complete allergy intolerance CSV dict.
@pytest.fixture
def allergy_intolerance_complete():
    return {
        "patientInternalId": "ABC",
        "accountNumber": "1234",
        "ssn": "111-11-111",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "mrn": "ABC1234",
        "encounterInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "resourceInternalId": "1-YTZ",
        "assigningAuthority": "hospa",
        "allergyCategory": "medication",
        "allergyType": "allergy",
        "allergyRecordedDateTime": "2021-10-11T20:53:00.000Z",
        "allergyCode": "1798007",
        "allergyCodeSystem": "http://snomed.info/sct",
        "allergyCodeText": "Hemoglobin Hammersmith",
        "allergyCriticality": "low",
        # Test a ManifestationCode without a list in this data
        "allergyManifestationCode": "368009",
        "allergyManifestationSystem": "http://hl7.org/fhir/ValueSet/clinical-findings",
        "allergyManifestationText": "Heart valve disorder",
        # purposely no clinicalStatusCode to confirm one is created
        "allergyVerificationStatusCode": "unconfirmed",
        "allergyOnsetStartDateTime": "2018-10-29 00:00:00",
        "allergyOnsetEndDateTime": "2019-10-11 00:43:36",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0,
        "timeZone": "US/Eastern"  # simulate a timeZone for onsetPeriod
    }


# Expected allergy intolerance from the complete allergy intolerance csv dict.
@pytest.fixture
def expected_allergy_intolerance_complete():
    return {
        "resourceType": "AllergyIntolerance",
        "id": "1-YTZ",
        "identifier": [
            {
                "id": "PI.ABC",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "PI",
                        "display": "Patient internal identifier"
                    }],
                    "text": "Patient internal identifier",
                },
                "system": "urn:id:hospa",
                "value": "ABC"
            },
            {
                "id": "MR.ABC1234",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR",
                        "display": "Medical record number"
                    }],
                    "text": "Medical record number"
                },
                "system": "urn:id:hospa",
                "value": "ABC1234"
            },
            {
                "id": "AN.1234",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "AN",
                        "display": "Account number"
                    }],
                    "text": "Account number",
                },
                "system": "urn:id:hospa",
                "value": "1234"
            },
            {
                "id": "VN.ENC1",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "VN",
                        "display": "Visit number"
                    }],
                    "text": "Visit number"
                },
                "system": "urn:id:hospa",
                "value": "ENC1"
            },
            {
                "id": "RI.1-YTZ",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "RI",
                        "display": "Resource identifier"
                    }],
                    "text": "Resource identifier"
                },
                "system": "urn:id:hospa",
                "value": "1-YTZ"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "1798007-SNOMED"
            },
        ],
        "type": "allergy",
        "category": ["medication"],
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "1798007"
            }],
            "text": "Hemoglobin Hammersmith"
        },
        "patient": {"reference": "Patient/ABC"},
        "encounter": {"reference": "Encounter/hospa-ENC1"},
        "recordedDate": "2021-10-11T20:53:00+00:00",
        "criticality": "low",
        "reaction": [{
            "manifestation": [{
                "coding": [{
                    "system": "http://hl7.org/fhir/ValueSet/clinical-findings",
                    "code": "368009"
                }],
                "text": "Heart valve disorder"}],
        }],
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                "code": "active",
                "display": "Active"
            }],
            "text": "Active"},
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                "code": "unconfirmed",
                "display": "Unconfirmed"
            }],
            "text": "Unconfirmed"
        },
        "onsetPeriod": {
            "start": "2018-10-29T00:00:00-04:00",
            "end": "2019-10-11T00:43:36-04:00"
        }
    }


# Tests the basic allergy intolerance, but checks that default clinicalStatus is set
def test_allergy_intolerance_basic_default_status(
    allergy_intolerance_basic, expected_allergy_intolerance_basic
):
    group_by_key = allergy_intolerance_basic.get("accountNumber")
    result_data: List = convert_record(group_by_key, allergy_intolerance_basic)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_record: AllergyIntolerance = AllergyIntolerance.parse_obj(
        result_data[0].dict()
    )

    assert fhir_record.resource_type == "AllergyIntolerance"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 3  # Account Number, VN and extID
    expected_resource = AllergyIntolerance(**expected_allergy_intolerance_basic)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

# Tests the basic allergy intolerance, but we set our own clinicalStatus and verificationStatus


def test_allergy_intolerance_basic_set_status(
    allergy_intolerance_basic, expected_allergy_intolerance_basic
):
    group_by_key = allergy_intolerance_basic.get("accountNumber")

    # Add clinicalStatus and verificationStatus to basic input for test
    allergy_intolerance_basic["allergyClinicalStatusCode"] = "resolved"
    allergy_intolerance_basic["allergyVerificationStatusCode"] = "confirmed"

    result_data: List = convert_record(group_by_key, allergy_intolerance_basic)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_record: AllergyIntolerance = AllergyIntolerance.parse_obj(
        result_data[0].dict()
    )

    assert fhir_record.resource_type == "AllergyIntolerance"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 3  # Account Number, VN and extID

    # Add clinicalStatus and verificationStatus to basic results for test
    expected_allergy_intolerance_basic["clinicalStatus"] = {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                "code": "resolved",
                "display": "Resolved"
            }
        ],
        "text": "Resolved",
    }
    expected_allergy_intolerance_basic["verificationStatus"] = {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                "code": "confirmed",
                "display": "Confirmed"
            }
        ],
        "text": "Confirmed"
    }

    expected_resource = AllergyIntolerance(**expected_allergy_intolerance_basic)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

# Tests the complete allergy intolerance


def test_allergy_intolerance_complete(
    allergy_intolerance_complete, expected_allergy_intolerance_complete
):
    group_by_key = allergy_intolerance_complete.get("accountNumber")
    result_data: List = convert_record(group_by_key, allergy_intolerance_complete)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_record: AllergyIntolerance = AllergyIntolerance.parse_obj(
        result_data[0].dict()
    )
    assert fhir_record.resource_type == "AllergyIntolerance"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 6  # Account Number, SSN and DL
    expected_resource = AllergyIntolerance(**expected_allergy_intolerance_complete)
    exclude_regex = [r"root\['id'\]"]

    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff
