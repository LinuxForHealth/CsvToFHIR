from importlib.resources import Resource
from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.medicationadministration import MedicationAdministration
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medicationstatement import MedicationStatement

from linuxforhealth.csvtofhir.fhirrs.medication_administration import \
    convert_record as ma_convert_record
from linuxforhealth.csvtofhir.fhirrs.medication_request import \
    convert_record as mr_convert_record


@pytest.fixture
def medication_use_missing_values():
    return {
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "mrn": "M1111-1",
        "medicationUseStatus": "in-progress",
        "patientInternalId": "111_M1111",
        "medicationRxNumber": "Rx12345",
        "encounterNumber": "E1111",
        "encounterInternalId": "111_E1111",
        "medicationCategoryCode": "inpatient",
        "medicationUseOccuranceDateTime": None,
        "medicationUseDosageText": None,
        "medicationUseDosageUnit": None,
        "medicationCodeText": "MELATONIN5 MG",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def other_medication_use_record_sample():
    return {
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "encounterNumber": "E1111",
        "encounterInternalId": "111_E1111",
        "medicationUseOccuranceDateTime": "2021-10-17T10:03:00.000Z",
        "medicationUseRouteText": "IV",
        "medicationUseRouteList": ["IV", "47625008^Intravenous route^SNOMED"],
        "medicationUseDosageText": "SCH",
        "medicationUseDosageUnit": "MG",
        "medicationUseStatus": "completed",
        "medicationCode": "641602225",
        "medicationCodeSystem": "http://hl7.org/fhir/sid/ndc",
        "medicationCodeText": "FAMOTIDINE 20MG VIAL",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def medication_use_record_sample():
    return {
        "assigningAuthority": "systemName",
        "patientInternalId": "100",
        "medicationCode": "834023",
        "medicationCodeDisplay": "Medrol",
        "medicationCodeSystem": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "medicationCodeText": "Medrol dosepak",
        "medicationUseStatus": "completed",
        "medicationAuthoredOn": "2020-01-23T12:34:56",
        "medicationRefills": "4",
        "medicationQuantity": "100",
        "medicationUseDosageText": "Use as directed",
        "medicationUseRouteCode": "26643006",
        "medicationUseRouteCodeSystem": "http://snomed.info/sct",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1,
        "timeZone": "US/Eastern"
    }


@pytest.fixture
def medication_use_with_list_of_codes():
    return {
        "assigningAuthority": "tenant1",
        "patientInternalId": "100",
        "medicationCode": "834023",
        "medicationCodeDisplay": "Medrol",
        "medicationCodeSystem": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "medicationCodeText": "Medrol dosepak",
        "medicationCodeList": ["Drug1", "Drug2^display2^", "Drug3^display3^urn:id:test", "Drug4^^NDC"],
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_rs_medication_statement_missing_values():
    return {
        "resourceType": "MedicationStatement",
        "id": "aa99dede",
        "identifier": [
            {
                "id": "PI.111-M1111",
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
                "system": "urn:id:111",
                "value": "111_M1111"
            },
            {
                "id": "MR.M1111-1",
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
                "system": "urn:id:111",
                "value": "M1111-1"
            },
            {
                "id": "AN.111-E1111",
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
                "system": "urn:id:111",
                "value": "111_E1111"
            },
            {
                "id": "VN.E1111",
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
                "system": "urn:id:111",
                "value": "E1111"
            },
            {
                "id": "RXN.Rx12345",
                "type": {
                    "coding": [
                        {
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/identifier-type",
                            "code": "RXN",
                            "display": "Prescription Number"
                        }
                    ],
                    "text": "Prescription Number"
                },
                "system": "urn:id:111",
                "value": "Rx12345"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "MELATONIN5 MG"
            }
        ],
        "status": "unknown",
        "medicationCodeableConcept": {"text": "MELATONIN5 MG"},
        "subject": {"reference": "Patient/111-M1111"},
        "context": {"reference": "Encounter/111-E1111"}
    }


@pytest.fixture
def expected_rs_medication_administration_missing_values():
    return {
        "resourceType": "MedicationAdministration",
        "id": "generated.id",
        "identifier": [
            {
                "id": "PI.111-M1111",
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
                "system": "urn:id:111",
                "value": "111_M1111"
            },
            {
                "id": "AN.111-E1111",
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
                "system": "urn:id:111",
                "value": "111_E1111"
            },
            {
                "id": "VN.E1111",
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
                "system": "urn:id:111",
                "value": "E1111"
            },
            {
                "id": "MR.M1111-1",
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
                "system": "urn:id:111",
                "value": "M1111-1"
            },
            {
                "id": "RXN.Rx12345",
                "type": {
                    "coding": [
                        {
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/identifier-type",
                            "code": "RXN",
                            "display": "Prescription Number"
                        }
                    ],
                    "text": "Prescription Number"
                },
                "system": "urn:id:111",
                "value": "Rx12345"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "MELATONIN5 MG"
            }
        ],
        "status": "in-progress",
        "subject": {"reference": "Patient/111-M1111"},
        "medicationCodeableConcept": {"text": "MELATONIN5 MG"},
        "context": {"reference": "Encounter/111-E1111"},
        "effectiveDateTime": "2021-10-17T10:03:00+00:00"
    }


@pytest.fixture
def expected_rs_medication_administration():
    return {
        "resourceType": "MedicationAdministration",
        "id": "generated.id",
        "identifier": [
            {
                "id": "AN.111-E1111",
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
                "system": "urn:id:111",
                "value": "111_E1111"
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
                "system": "urn:id:111",
                "value": "E1111",
                "id": "VN.E1111"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "641602225-NDC"
            }
        ],
        "status": "completed",
        "subject": {"reference": "Patient/111-E1111"},
        "medicationCodeableConcept": {
            "coding": [{"code": "641602225", "system": "http://hl7.org/fhir/sid/ndc"}],
            "text": "FAMOTIDINE 20MG VIAL"
        },
        "context": {"reference": "Encounter/111-E1111"},
        "effectiveDateTime": "2021-10-17T10:03:00+00:00",
        "dosage": {
            "text": "SCH",
            "route": {
                "coding": [
                    {
                        "code": "IV",
                        "system": "urn:id:111"
                    },
                    {
                        "code": "47625008",
                        "display": "Intravenous route",
                        "system": "http://snomed.info/sct"
                    }
                ],
                "text": "IV"
            },
            "dose": {
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason",
                        "valueCode": "as-text"
                    }
                ]
            }
        }
    }


@pytest.fixture
def expected_rs_medication_request():
    return {
        "authoredOn": "2020-01-23T12:34:56-05:00",
        "dispenseRequest": {
            "numberOfRepeatsAllowed": 4,
            "quantity": {
                "value": 100
            }
        },
        "dosageInstruction": [
            {
                "route": {
                    "coding": [
                        {
                            "code": "26643006",
                            "system": "http://snomed.info/sct"
                        }
                    ]
                },
                "text": "Use as directed"
            }
        ],
        "id": "generated.id",
        "identifier": [
            {
                "id": "PI.100",
                "system": "urn:id:systemName",
                "type": {
                    "coding": [
                        {
                            "code": "PI",
                            "display": "Patient internal identifier",
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203"
                        }
                    ],
                    "text": "Patient internal identifier"
                },
                "value": "100"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "834023-RXNORM"
            }
        ],
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "code": "834023",
                    "display": "Medrol",
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm"
                }
            ],
            "text": "Medrol dosepak"
        },
        "resourceType": "MedicationRequest",
        "status": "completed",
        "subject": {
            "reference": "Patient/100"
        }
    }


@pytest.fixture
def expected_rs_medication_request_code_list():
    return {
        "id": "generated.id",
        "identifier": [
            {
                "id": "PI.100",
                "system": "urn:id:tenant1",
                "type": {
                    "coding": [
                        {
                            "code": "PI",
                            "display": "Patient internal identifier",
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203"
                        }
                    ],
                    "text": "Patient internal identifier"
                },
                "value": "100"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "834023-RXNORM"
            }
        ],
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "code": "834023",
                    "display": "Medrol",
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm"
                }, {
                    "code": "Drug1",
                    "system": "urn:id:tenant1"
                }, {
                    "code": "Drug2",
                    "display": "display2",
                    "system": "urn:id:tenant1"
                }, {
                    "code": "Drug3",
                    "display": "display3",
                    "system": "urn:id:test"
                }, {
                    "code": "Drug4",
                    "system": "http://hl7.org/fhir/sid/ndc"
                }

            ],
            "text": "Medrol dosepak"
        },
        "resourceType": "MedicationRequest",
        "status": "unknown",
        "subject": {
            "reference": "Patient/100"
        }
    }


def test_convert_record_missing_values(
    medication_use_missing_values, expected_rs_medication_statement_missing_values
):
    group_by_key = medication_use_missing_values.get("accountNumber")

    results: List[Resource] = ma_convert_record(
        group_by_key, medication_use_missing_values, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    # because date of administring medication is missing, the resource was changed to Medication Statement
    assert result.resource_type == "MedicationStatement", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert len(result.identifier) == 6, "Identifier count is incorrect"
    fhir_result: MedicationStatement = MedicationStatement.parse_obj(result.dict())

    expected_resource = MedicationStatement(
        **expected_rs_medication_statement_missing_values
    )

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    )
    assert diff == {}


def test_convert_medication_administration_missing_values(
    medication_use_missing_values, expected_rs_medication_administration_missing_values
):
    group_by_key = medication_use_missing_values.get("accountNumber")
    medication_use_missing_values[
        "medicationUseOccuranceDateTime"
    ] = "2021-10-17T10:03:00.000Z"
    results: List[Resource] = ma_convert_record(
        group_by_key, medication_use_missing_values, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]
    # because date of administering medication is missing, the resource was changed to Medication Statement
    assert result.resource_type == "MedicationAdministration", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert len(result.identifier) == 6, "Identifier count is incorrect"

    fhir_result: MedicationAdministration = MedicationAdministration.parse_obj(
        result.dict()
    )

    expected_resource = MedicationAdministration(
        **expected_rs_medication_administration_missing_values
    )

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}


def test_convert_medication_administration(
    other_medication_use_record_sample, expected_rs_medication_administration
):
    group_by_key = other_medication_use_record_sample.get("accountNumber")
    results: List[Resource] = ma_convert_record(
        group_by_key, other_medication_use_record_sample, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    # because date of administering medication is missing, the resource was changed to Medication Statement
    assert result.resource_type == "MedicationAdministration", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert len(result.identifier) == 3, "Identifier count is incorrect"
    fhir_result: MedicationAdministration = MedicationAdministration.parse_obj(
        result.dict()
    )

    expected_resource = MedicationAdministration(
        **expected_rs_medication_administration
    )

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    )
    assert diff == {}


def test_convert_medication_request(
    medication_use_record_sample, expected_rs_medication_request
):
    group_by_key = medication_use_record_sample.get("patientInternalId")
    results: List[Resource] = mr_convert_record(
        group_by_key, medication_use_record_sample, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "MedicationRequest", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert len(result.identifier) == 2, "Identifier count is incorrect"
    fhir_result: MedicationRequest = MedicationRequest.parse_obj(
        result.dict()
    )

    expected_resource = MedicationRequest(
        **expected_rs_medication_request
    )

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    )
    assert diff == {}


def test_convert_medication_request_code_list(
    medication_use_with_list_of_codes, expected_rs_medication_request_code_list
):
    group_by_key = medication_use_with_list_of_codes.get("patientInternalId")
    results: List[Resource] = mr_convert_record(
        group_by_key, medication_use_with_list_of_codes, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    # because date of administering medication is missing, the resource was changed to Medication Statement
    assert result.resource_type == "MedicationRequest", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert len(result.identifier) == 2, "Identifier count is incorrect"
    fhir_result: MedicationRequest = MedicationRequest.parse_obj(
        result.dict()
    )

    expected_resource = MedicationRequest(
        **expected_rs_medication_request_code_list
    )

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    )
    assert diff == {}
