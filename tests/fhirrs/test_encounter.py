
from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.location import Location
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record


@pytest.fixture
def encounter_record_basic():
    return {
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "patientInternalId": "111_M1111",
        "encounterNumber": "E1111",
        "resourceInternalId": "111_E1111",
        "encounterStatus": None,
        "hospitalizationDischargeDispositionCode": 1,
        "hospitalizationDischargeDispositionCodeText": "HOM",
        "hospitalizationDischargeDispositionCodeSystem": "http://terminology.hl7.org/CodeSystem/v2-0112",
        "hospitalizationReAdmissionCode": 1,
        "hospitalizationAdmitSourceCodeText": "Outpatient",
        "encounterClassCode": "EMER",
        "encounterClassText": "ER",
        "encounterStartDateTime": "2021-10-14T17:19:00.000Z",
        "encounterEndDateTime": "2021-10-15T03:53:00.000Z",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_record_basic():
    return {
        "resourceType": "Encounter",
        "id": "111-E1111",
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
                "id": "RI.111-E1111",
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
                "system": "urn:id:111",
                "value": "111_E1111"
            },
        ],
        "status": "unknown",
        "subject": {"reference": "Patient/111-M1111"},
        "period": {
            "start": "2021-10-14T17:19:00+00:00",
            "end": "2021-10-15T03:53:00+00:00"
        },
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "EMER",
            "display": "ER"
        },
        "hospitalization": {
            "admitSource": {"text": "Outpatient"},
            "reAdmission": {
                "coding": [{"code": "R", "display": "Re-admission"}],
                "text": "Re-admission"
            },
            "dischargeDisposition": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0112",
                        "code": "1"
                    }
                ],
                "text": "HOM"
            }
        }
    }


def test_convert_record_encounter_basic(
    encounter_record_basic, expected_encounter_record_basic
):
    group_by_key = encounter_record_basic.get("accountNumber")

    result: List[Resource] = convert_record(group_by_key, encounter_record_basic, None)
    assert len(result) == 1
    encounter = result[0]
    # loading into fhir.resource test validity of the object
    fhir_result: Encounter = Encounter.parse_obj(encounter.dict())

    assert fhir_result.resource_type == "Encounter"
    assert fhir_result.identifier
    assert len(fhir_result.identifier) == 4  # Account Number, SSN and DL

    expected_resource = Encounter(**expected_encounter_record_basic)
    diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
    assert diff == {}


@pytest.fixture
def encounter_record_full():
    return {
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "patientInternalId": "111_M1111",
        "ssn": "000-00-0000",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "mrn": "MRN-1234564",
        "encounterNumber": "E1111",
        "resourceInternalId": "111_E1111",
        "encounterStatus": "in-progress",
        "encounterClassCode": "AMB",
        "encounterClassText": "ambulatory",
        "encounterClassSystem": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "encounterPriorityCode": "R",
        "encounterStartDateTime": "2021-10-14T13:19:00.000Z",
        "encounterLengthValue": 30,
        "encounterLengthUnits": "minutes",
        "encounterReasonCode": "5902003",
        "encounterReasonCodeSystem": "http://snomed.info/sct",
        "encounterReasonCodeText": "Physical Examination",
        "encounterParticipantSequenceId": "Primary",
        "encounterStatusHistory": [
            "arrived^2018-06-21 15:03:46Z^None",
            "planned^2018-06-20 00:00:00Z^2018-06-21 15:03:46Z"],
        "practitionerInternalId": "PRA-4879",
        "practitionerNPI": "NPI1234567",
        "practitionerNameLast": "SUMMERS",
        "practitionerNameFirst": "JAKE",
        "practitionerGender": "male",
        "practitionerRoleText": "Primary",
        "practitionerSpecialtyText": "Family Medicine",
        "locationResourceInternalId": "LOC1234",
        "locationName": "Quincy Office",
        "locationTypeCode": "OF",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_encounter_full():
    return {
        "resourceType": "Encounter",
        "id": "111-E1111",
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
                "id": "MR.MRN-1234564",
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
                "value": "MRN-1234564"
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
                "id": "RI.111-E1111",
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
                "system": "urn:id:111",
                "value": "111_E1111"
            },
        ],
        "status": "in-progress",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory"
        },
        "priority": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                    "code": "R"
                }
            ]
        },
        "subject": {"reference": "Patient/111-M1111"},
        "participant": [
            {"id": "Primary", "individual": {"reference": "PractitionerRole/PRA-4879"}}
        ],
        "period": {"start": "2021-10-14T13:19:00+00:00"},
        "length": {"value": "30", "unit": "minutes"},
        "reasonCode": [
            {
                "coding": [{"system": "http://snomed.info/sct", "code": "5902003"}],
                "text": "Physical Examination"
            }
        ],
        "location": [
            {
                "location": {
                    "reference": "Location/LOC1234",
                    "display": "Quincy Office"
                }
            }
        ],
        "statusHistory": [
            {
                "status": "arrived",
                "period": {
                    "start": "2018-06-21T15:03:46"
                }
            },
            {
                "status": "planned",
                "period": {
                    "start": "2018-06-20T00:00:00",
                    "end": "2018-06-21T15:03:46"
                }
            }
        ],
    }


@pytest.fixture
def expected_practitioner_full():
    return {
        "resourceType": "Practitioner",
        "id": "PRA-4879",
        "identifier": [
            {
                "id": "RI.PRA-4879",
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
                "system": "urn:id:111",
                "value": "PRA-4879"
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
                "value": "NPI1234567"
            },
        ],
        "name": [{"text": "JAKE SUMMERS", "family": "SUMMERS", "given": ["JAKE"]}],
        "gender": "male"
    }


@pytest.fixture
def expected_practitioner_role_full():
    return {
        "resourceType": "PractitionerRole",
        "id": "PRA-4879",
        "identifier": [
            {
                "id": "RI.PRA-4879",
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
                "system": "urn:id:111",
                "value": "PRA-4879"
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
                "value": "NPI1234567"
            },
        ],
        "specialty": [{"text": "Family Medicine", "id": "Family-Medicine"}],
        "code": [{"text": "Primary", "id": "Primary"}],
        "practitioner": {
            "reference": "Practitioner/PRA-4879",
            "display": "JAKE SUMMERS"
        }
    }


@pytest.fixture
def expected_location_full():
    return {
        "resourceType": "Location",
        "id": "LOC1234",
        "identifier": [
            {
                "id": "RI.LOC1234",
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
                "system": "urn:id:111",
                "value": "LOC1234"
            }
        ],
        "name": "Quincy Office",
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "OF"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def expected_patient_full():
    return {
        "resourceType": "Patient",
        "id": "111-M1111",
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
                "id": "MR.MRN-1234564",
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
                "value": "MRN-1234564"
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
            }
        ]
    }


def test_convert_record_encounter_full(
    encounter_record_full,
    expected_patient_full,
    expected_encounter_full,
    expected_practitioner_full,
    expected_practitioner_role_full,
    expected_location_full,
):
    group_by_key = encounter_record_full.get("accountNumber")

    results: List[Resource] = convert_record(group_by_key, encounter_record_full, None)
    assert len(results) == 5, "Unexpected resource count generated"
    expected_resource_list = [
        "Patient",
        "Encounter",
        "Practitioner",
        "PractitionerRole",
        "Location"
    ]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "Encounter":
            assert (
                len(result.identifier) == 5
            ), "Encounter: identifier count is incorrect"
            expected_resource = Encounter(**expected_encounter_full)
            fhir_result: Encounter = Encounter.parse_obj(result.dict())
        elif rs_type == "Patient":
            assert (
                len(result.identifier) == 3
            ), "Patient: identifier count is incorrect"
            expected_resource = Patient(**expected_patient_full)
            fhir_result: Patient = Patient.parse_obj(result.dict())
        elif rs_type == "Practitioner":
            assert (
                len(result.identifier) == 2
            ), "Practitioner: identifier count is incorrect"
            expected_resource = Practitioner(**expected_practitioner_full)
            fhir_result: Practitioner = Practitioner.parse_obj(result.dict())
        elif rs_type == "PractitionerRole":
            assert (
                len(result.identifier) == 2
            ), "PractitionerRole: identifier count is incorrect"
            expected_resource = PractitionerRole(**expected_practitioner_role_full)
            fhir_result: PractitionerRole = PractitionerRole.parse_obj(
                result.dict()
            )
        elif rs_type == "Location":
            assert (
                len(result.identifier) == 1
            ), "Location: identifier count is incorrect"
            expected_resource = Location(**expected_location_full)
            fhir_result: Location = Location.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        diff = DeepDiff(expected_resource, fhir_result, ignore_order=True)
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )
