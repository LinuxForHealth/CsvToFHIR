from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_add_participant_info():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterParticipantTypeText": "attender",
        "encounterParticipantTypeCode": "ATND",
        "encounterParticipantSequenceId": "ATTEND^ABC1234",
        "practitionerNPI": "NPI1234",
        "practitionerInternalId": "ABC1234",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_participant_only():
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
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-ENC1"},
        "participant": [
            {
                "id": "ATTEND-ABC1234",
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                "display": "attender",
                                "code": "ATND"
                            }
                        ],
                        "text": "attender"
                    }
                ],
                "individual": {"reference": "Practitioner/ABC1234"}
            }
        ]
    }


@pytest.fixture
def encounter_practitioner():
    return {
        "resourceType": "Practitioner",
        "id": "ABC1234",
        "identifier": [
            {
                "id": "RI.ABC1234",
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
                "value": "ABC1234"
            },
            {
                "id": "NPI",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "NPI",
                            "display": "National provider identifier"
                        }
                    ],
                    "text": "National provider identifier"
                },
                "value": "NPI1234"
            }
        ]
    }


@pytest.fixture
def encounter_record_participant_no_sequence_id():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterParticipantTypeText": "attender",
        "encounterParticipantTypeCode": "ATND",
        "practitionerNPI": "NPI1234",
        "practitionerInternalId": "ABC1234",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_participant_no_sequence_id():
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
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospa-ENC1"},
        "participant": [
            {
                "id": "ATND.NPI.NPI1234",
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                "display": "attender",
                                "code": "ATND"
                            }
                        ],
                        "text": "attender"
                    }
                ],
                "individual": {
                    "reference": "Practitioner/ABC1234"
                }
            }
        ]
    }


@pytest.fixture
def encounter_record_general_practitioner_test():
    return {
        "assigningAuthority": "hospa",
        "accountNumber": "hospa_ENC1",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "encounterParticipantTypeText": "PRIMARY_CARE",
        "practitionerRoleText": "PRIMARY_CARE",
        "encounterParticipantTypeCode": "PRIMARY_CARE",
        "encounterParticipantTypeCodeSystem": "codeSystem",
        "practitionerNPI": "NPI1234",
        "practitionerInternalId": "ABC1234",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_general_practitioner_test():
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
            }
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {
            "reference": "Patient/hospa-ENC1"
        },
        "participant": [
            {
                "id": "PRIMARY-CARE.NPI.NPI1234",
                "type": [
                    {
                        "coding": [
                            {
                                "system": "urn:id:codeSystem",
                                "code": "PRIMARY_CARE"
                            }
                        ],
                        "text": "PRIMARY_CARE"
                    }
                ],
                "individual": {
                    "reference": "PractitionerRole/ABC1234"
                }
            }
        ]
    }


@pytest.fixture
def expected_practitioner_role_general_practitioner_test():
    return {
        "resourceType": "PractitionerRole",
        "id": "ABC1234",
        "identifier": [
            {
                "id": "RI.ABC1234",
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
                "value": "ABC1234"
            },
            {
                "id": "NPI",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "NPI",
                            "display": "National provider identifier"
                        }
                    ],
                    "text": "National provider identifier"
                },
                "value": "NPI1234"
            }
        ],
        "code": [
            {
                "id": "PRIMARY-CARE",
                "text": "PRIMARY_CARE"
            }
        ]
    }


@pytest.fixture
def expected_patient_general_practitioner_test():
    return {
        "resourceType": "Patient",
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
                "value": "hospa_ENC1"
            }
        ],
        "generalPractitioner": [
            {
                "reference": "PractitionerRole/ABC1234"
            }
        ]
    }


def test_convert_record_encounter_participant_row(
    encounter_record_add_participant_info,
    expected_encounter_participant_only,
    encounter_practitioner,
):
    group_by_key = encounter_record_add_participant_info.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_add_participant_info, None
    )

    assert len(results) == 2, "Unexpected resource count generated"
    expected_resource_list = ["Encounter", "Practitioner"]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "Encounter":
            assert (
                len(result.identifier) == 3
            ), "Encounter: identifier count is incorrect"
            expected_resource = Encounter(**expected_encounter_participant_only)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "Practitioner":
            assert (
                len(result.identifier) == 2
            ), "Location: identifier count is incorrect"
            expected_resource = Practitioner(**encounter_practitioner)
            fhir_result: Practitioner = Practitioner.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )


def test_convert_record_encounter_participant_no_sequence_id(
    encounter_record_participant_no_sequence_id,
    expected_encounter_participant_no_sequence_id,
    encounter_practitioner,
):
    group_by_key = encounter_record_participant_no_sequence_id.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_participant_no_sequence_id, None
    )

    assert len(results) == 2, "Unexpected resource count generated"
    expected_resource_list = ["Encounter", "Practitioner"]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "Encounter":
            assert (
                len(result.identifier) == 3
            ), "Encounter: identifier count is incorrect"
            expected_resource = Encounter(**expected_encounter_participant_no_sequence_id)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "Practitioner":
            assert (
                len(result.identifier) == 2
            ), "Location: identifier count is incorrect"
            expected_resource = Practitioner(**encounter_practitioner)
            fhir_result: Practitioner = Practitioner.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )


def test_convert_record_general_practitioner_test(
    encounter_record_general_practitioner_test,
    expected_encounter_general_practitioner_test,
    expected_practitioner_role_general_practitioner_test,
    expected_patient_general_practitioner_test
):
    group_by_key = encounter_record_general_practitioner_test.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_general_practitioner_test, None
    )

    assert len(results) == 3, "Unexpected resource count generated"
    expected_resource_list = ["Encounter", "PractitionerRole", "Patient"]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "Encounter":
            assert (
                len(result.identifier) == 3
            ), "Encounter: identifier count is incorrect"
            expected_resource = Encounter(**expected_encounter_general_practitioner_test)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "PractitionerRole":
            assert (
                len(result.identifier) == 2
            ), "PractitionerRole: identifier count is incorrect"
            expected_resource = PractitionerRole(**expected_practitioner_role_general_practitioner_test)
            fhir_result: PractitionerRole = PractitionerRole.parse_obj(result.dict())
        elif rs_type == "Patient":
            # Should be an AN identifier
            assert (
                len(result.identifier) == 1
            ), "Patient: identifier count is incorrect"
            expected_resource = Patient(**expected_patient_general_practitioner_test)
            fhir_result: Patient = Patient.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )
