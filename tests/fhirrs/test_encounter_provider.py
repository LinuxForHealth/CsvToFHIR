from typing import List

import pytest
from tests.support import deep_diff
from fhir.resources.encounter import Encounter
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_add_provider_info():
    return {
        "patientInternalId": "100",
        "practitionerInternalId": "12345",
        "encounterInternalId": "100103",
        "resourceInternalId": "12345",
        "practitionerGender": "male",
        "encounterParticipantTypeCode": "REF",
        "practitionerRoleCode": "309343006",
        "practitionerRoleCodeSystem": "http://snomed.info/sct",
        "practitionerSpecialtyCodeList": [
            "OneCode^OneDisplay^OneSystem",
            "TwoCode^TwoDisplay^TwoSystem",
            "ThreeCode^ThreeDisplay^ThreeSystem",
            "FourCode^FourDisplay^FourSystem",
            "FiveCode^FiveDisplay^FiveSystem"],
        "practitionerSpecialtyCodeSystem": "http://hl7.org/fhir/practitioner-specialty",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1,
    }


# TODO: Fix participant.id
@pytest.fixture
def expected_encounter():
    return {
        "resourceType": "Encounter",
        "id": "100103",
        "identifier": [
            {
                "id": "PI.100",
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
                "value": "100"
            },
            {
                "id": "RI.100103",
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
                "value": "100103"
            }
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {
            "reference": "Patient/100"
        },
        "participant": [
            {
                "id": "REF.RI.12345",
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                "code": "REF",
                                "display": "referrer"
                            }
                        ],
                        "text": "referrer"
                    }
                ],
                "individual": {
                    "reference": "PractitionerRole/12345"
                }
            }
        ]
    }


@pytest.fixture
def expected_practitioner():
    return {
        "resourceType": "Practitioner",
        "id": "12345",
        "identifier": [
            {
                "id": "RI.12345",
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
                "value": "12345"
            }
        ],
        "gender": "male"
    }


@pytest.fixture
def expected_practitioner_role():
    return {
        "resourceType": "PractitionerRole",
        "id": "12345",
        "identifier": [
            {
                "id": "RI.12345",
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
                "value": "12345"
            }
        ],
        "practitioner": {
            "reference": "Practitioner/12345"
        },
        "code": [
            {
                "id": "309343006",
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "309343006"
                    }
                ]
            }
        ],
        "specialty": [
            {
                "id": "OneCode",
                "coding": [
                    {
                        "system": "urn:id:OneSystem",
                        "code": "OneCode",
                        "display": "OneDisplay"
                    }
                ],
                "text": "OneDisplay"
            },
            {
                "id": "TwoCode",
                "coding": [
                    {
                        "system": "urn:id:TwoSystem",
                        "code": "TwoCode",
                        "display": "TwoDisplay"
                    }
                ],
                "text": "TwoDisplay"
            },
            {
                "id": "ThreeCode",
                "coding": [
                    {
                        "system": "urn:id:ThreeSystem",
                        "code": "ThreeCode",
                        "display": "ThreeDisplay"
                    }
                ],
                "text": "ThreeDisplay"
            },
            {
                "id": "FourCode",
                "coding": [
                    {
                        "system": "urn:id:FourSystem",
                        "code": "FourCode",
                        "display": "FourDisplay"
                    }
                ],
                "text": "FourDisplay"
            },
            {
                "id": "FiveCode",
                "coding": [
                    {
                        "system": "urn:id:FiveSystem",
                        "code": "FiveCode",
                        "display": "FiveDisplay"
                    }
                ],
                "text": "FiveDisplay"
            }
        ]
    }


def test_convert_record_encounter_provider_row(
    encounter_record_add_provider_info,
    expected_encounter,
    expected_practitioner,
    expected_practitioner_role,
):
    group_by_key = encounter_record_add_provider_info.get("patient_id")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_add_provider_info, None
    )

    assert len(results) == 3, "Unexpected resource count generated"
    expected_resource_list = ["Encounter", "Practitioner", "PractitionerRole"]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "Encounter":
            expected_resource = Encounter(**expected_encounter)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "Practitioner":
            expected_resource = Practitioner(
                **expected_practitioner
            )
            fhir_result: Practitioner = Practitioner.parse_obj(result.dict())
        elif rs_type == "PractitionerRole":
            expected_resource = PractitionerRole(
                **expected_practitioner_role
            )
            fhir_result: PractitionerRole = PractitionerRole.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        compare_result = deep_diff(expected_resource.dict(), fhir_result.dict())
        assert compare_result == {}

    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )
