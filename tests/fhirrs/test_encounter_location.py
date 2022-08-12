from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.location import Location
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_location_update():
    return {
        "assigningAuthority": "hospa",
        "resourceInternalId": "hospa_ENC1",
        "encounterNumber": "ENC1",
        "accountNumber": "hospa_ENC1",
        "locationName": "LOC#ER",
        "encounterLocationSequenceId": "1",
        "encounterLocationPeriodStart": "2021-10-10T14:53:00.000Z",
        "locationTypeText": "Trauma Unit",
        "locationTypeCode": "ETU",
        "locationResourceInternalId": "LOC#ER",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_location_update():
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
        "location": [
            {
                "id": "1",
                "location": {
                    "reference": "Location/LOC-ER",
                    "display": "LOC#ER"
                },
                "period": {
                    "start": "2021-10-10T14:53:00+00:00"
                }
            }
        ]
    }


@pytest.fixture
def expected_location_entry():
    return {
        "resourceType": "Location",
        "id": "LOC-ER",
        "identifier": [
            {
                "id": "RI.LOC-ER",
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
                "value": "LOC#ER"
            }
        ],
        "name": "LOC#ER",
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "ETU"
                    }
                ],
                "text": "Trauma Unit"
            }
        ],
    }


def test_convert_encounter_location_only_row(
    encounter_record_location_update,
    expected_encounter_location_update,
    expected_location_entry,
):
    group_by_key = encounter_record_location_update.get("accountNumber")

    results: List[Resource] = convert_record(
        group_by_key, encounter_record_location_update, None
    )

    assert len(results) == 2, "Unexpected resource count generated"
    expected_resource_list = ["Encounter", "Location"]
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
            expected_resource = Encounter(**expected_encounter_location_update)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "Location":
            assert (
                len(result.identifier) == 1
            ), "Location: identifier count is incorrect"
            expected_resource = Location(**expected_location_entry)
            fhir_result: Location = Location.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )
