from importlib.resources import Resource
from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.encounter import Encounter
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.procedure import Procedure
from fhir.resources.reference import Reference

from linuxforhealth.csvtofhir.fhirrs.procedure import convert_record


@pytest.fixture
def patient_pp_sample():
    return {
        "assigningAuthority": "hospb",
        "accountNumber": "hospb_1111",
        "encounterInternalId": "hospb_1111",
        "encounterNumber": "1111",
        "procedureCode": "5A1D70Z",
        "procedureCodeSystem": "http://hl7.org/fhir/sid/icd-10-cm",
        "procedureEncounterSequenceId": "1",
        "procedurePerformedDateTime": "2021-10-15T13:00:00.000Z",
        "practitionerInternalId": "ABCDE'F",
        "practitionerNPI": None,
        "practitionerRoleCode": "304292004",
        "practitionerRoleText": "Surgeon",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def expected_pp_encounter():
    return {
        "resourceType": "Encounter",
        "id": "hospb-1111",
        "identifier": [
            {
                "id": "RI.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "AN.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "VN.1111",
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
                "system": "urn:id:hospb",
                "value": "1111"
            }
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospb-1111"},
        "participant": [
            {
                "id": "RI.ABCDE-F",
                "individual": {"reference": "PractitionerRole/ABCDE-F"}
            }
        ],
        "reasonReference": [
            {
                "extension": [
                    {
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-sequence",
                        "valuePositiveInt": 1
                    }
                ],
                "id": "Procedure.id",
                "reference": "Procedure/Procedure.id"
            }
        ]
    }


@pytest.fixture
def expected_pp_practitioner_role():
    return {
        "resourceType": "PractitionerRole",
        "id": "ABCDE-F",
        "identifier": [
            {
                "id": "RI.ABCDE-F",
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
                "system": "urn:id:hospb",
                "value": "ABCDE'F"
            }
        ],
        "code": [
            {
                "coding": [{"system": "http://snomed.info/sct", "code": "304292004"}],
                "text": "Surgeon"
            }
        ]
    }


@pytest.fixture
def expected_pp_procedure_seqid_and_practitioner():
    return {
        "resourceType": "Procedure",
        "id": "31b59550-9",
        "identifier": [
            {
                "id": "AN.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "VN.1111",
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
                "system": "urn:id:hospb",
                "value": "1111"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "5A1D70Z-ICD10"
            }
        ],
        "status": "unknown",
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": "5A1D70Z"
            }]
        },
        "subject": {"reference": "Patient/hospb-1111"},
        "encounter": {"reference": "Encounter/hospb-1111"},
        "performedDateTime": "2021-10-15T13:00:00+00:00",
        "performer": [{"actor": {"reference": "PractitionerRole/ABCDE-F"}}]
    }


@pytest.fixture
def patient_hcpcs_sample():
    return {
        "assigningAuthority": "hospb",
        "accountNumber": "hospb_1111",
        "encounterInternalId": "hospb_1111",
        "encounterNumber": "1111",
        "procedureCode": "76000",
        "procedureCodeSystem": "http://www.ama-assn.org/go/cpt",
        "procedureModifierList": "TCFY",
        "procedureModifierSystem": "http://ibm.com/fhir/cdm/CodeSystem/procedure-modifier",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def expected_encounter_hcpcs():
    return {
        "resourceType": "Encounter",
        "id": "hospb-1111",
        "identifier": [
            {
                "id": "RI.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "AN.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "VN.1111",
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
                "system": "urn:id:hospb",
                "value": "1111"
            }
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/hospb-1111"},
        "reasonReference": [
            {"id": "Procedure.id", "reference": "Procedure/Procedure.id"}
        ]
    }


@pytest.fixture
def expected_procedure_hcpcs():
    return {
        "resourceType": "Procedure",
        "id": "31b59550-9",
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {"system": "http://ibm.com/fhir/cdm/CodeSystem/procedure-modifier", "code": "TC"}
                    ]
                }
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {"system": "http://ibm.com/fhir/cdm/CodeSystem/procedure-modifier", "code": "FY"}
                    ]
                }
            }
        ],
        "identifier": [
            {
                "id": "AN.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "VN.1111",
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
                "system": "urn:id:hospb",
                "value": "1111"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "76000-CPT"
            }
        ],
        "status": "unknown",
        "code": {
            "coding": [{
                "system": "http://www.ama-assn.org/go/cpt",
                "code": "76000"
            }]
        },
        "subject": {"reference": "Patient/hospb-1111"},
        "encounter": {"reference": "Encounter/hospb-1111"}
    }


@pytest.fixture
def patient_hcpcs_sample_no_modifier_system():
    return {
        "assigningAuthority": "hospb",
        "accountNumber": "hospb_1111",
        "encounterInternalId": "hospb_1111",
        "encounterNumber": "1111",
        "procedureCode": "76000",
        "procedureCodeSystem": "http://www.ama-assn.org/go/cpt",
        "procedureModifierList": "TCFY",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def expected_procedure_hcpcs_no_modifier_system():
    return {
        "resourceType": "Procedure",
        "id": "31b59550-9",
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {"code": "TC"}
                    ]
                }
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {"code": "FY"}
                    ]
                }
            }
        ],
        "identifier": [
            {
                "id": "AN.hospb-1111",
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
                "system": "urn:id:hospb",
                "value": "hospb_1111"
            },
            {
                "id": "VN.1111",
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
                "system": "urn:id:hospb",
                "value": "1111"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "76000-CPT"
            }
        ],
        "status": "unknown",
        "code": {
            "coding": [{
                "system": "http://www.ama-assn.org/go/cpt",
                "code": "76000"
            }]
        },
        "subject": {"reference": "Patient/hospb-1111"},
        "encounter": {"reference": "Encounter/hospb-1111"}
    }


@pytest.fixture
def procedure_input():
    return {
        "encounterInternalId": "100101",
        "patientInternalId": "100",
        "procedureCategorySystem": "http://snomed.info/sct",
        "procedureCode": "97113",
        "procedureCodeSystem": "http://www.ama-assn.org/go/cpt",
        "procedureModifierList": "59,GP",
        "procedureCodeList": ["229197007^^SNOMED", "97113^^CPT"],
        "procedureStatus": "COMPLETE",
        "procedurePerformedDateTime": "2013-10-29 00:00:00",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def procedure_output():
    return {
        "resourceType": "Procedure",
        "id": "1651874301445617000.84014993af274b67965fef54ce2c0371",
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "code": "59"
                        }
                    ]
                }
            },
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/procedure-modifier",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "code": "GP"
                        }
                    ]
                }
            }
        ],
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
                "id": "extID",
                "system": "urn:id:extID",
                "value": "97113-CPT"
            }
        ],
        "status": "COMPLETE",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "229197007"
                },
                {
                    "system": "http://www.ama-assn.org/go/cpt",
                    "code": "97113"
                }
            ]
        },
        "subject": {
            "reference": "Patient/100"
        },
        "encounter": {
            "reference": "Encounter/100101"
        },
        "performedDateTime": "2013-10-29T00:00:00"
    }


@pytest.fixture
def encounter_output():
    return {
        "resourceType": "Encounter",
        "id": "100101",
        "identifier": [
            {
                "id": "PI.100",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "PI",
                        "display": "Patient internal identifier"
                    }],
                    "text": "Patient internal identifier"
                },
                "value": "100"
            },
            {
                "id": "RI.100101",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "RI",
                        "display": "Resource identifier"
                    }],
                    "text": "Resource identifier"
                },
                "value": "100101"
            }
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/100"},
        "reasonReference": [{
            "id": "1652111685306147000.4c32a41bdcd347c8afc28e97ff64aa9b",
            "reference": "Procedure/1652111685306147000.4c32a41bdcd347c8afc28e97ff64aa9b"
        }]
    }


def test_procedure_seqid_practitioner(
    patient_pp_sample,
    expected_pp_procedure_seqid_and_practitioner,
    expected_pp_encounter,
    expected_pp_practitioner_role,
):
    group_by_key = patient_pp_sample.get("accountNumber")
    results: List[Resource] = convert_record(
        group_by_key, patient_pp_sample, None
    )
    assert results
    assert len(results) == 3, "Unexpected resource count generated"
    enc: Encounter = None
    proc: Procedure = None
    prrole: PractitionerRole = None
    for r in results:
        if r.resource_type == "Encounter":
            enc = r
            assert enc.identifier
            assert len(enc.identifier) == 3, "Encounter: Identifier count is incorrect"
        elif r.resource_type == "Procedure":
            proc = r
            assert proc.identifier
            assert len(proc.identifier) == 3, "Procedure: Identifier count is incorrect"
        elif r.resource_type == "PractitionerRole":
            prrole = r
            assert prrole.identifier
            assert (len(prrole.identifier) == 1), "Procedure: Identifier count is incorrect"
        else:
            assert False, "Unexpected resource type: " + r.json()

    fhir_procedure: Procedure = Procedure.parse_obj(proc.dict())
    fhir_encounter: Encounter = Encounter.parse_obj(enc.dict())
    expected_procedure = Procedure(
        **expected_pp_procedure_seqid_and_practitioner
    )
    expected_encounter = Encounter(**expected_pp_encounter)

    # setup encounter.reasonReference to have newly created procedure link
    reason_ref: Reference = expected_encounter.reasonReference[0]
    reason_ref.id = fhir_procedure.id
    reason_ref.reference = "Procedure/" + fhir_procedure.id

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_procedure.dict(),
        fhir_procedure.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}, "Procedure compare failed"

    diff = DeepDiff(
        expected_encounter.dict(),
        fhir_encounter.dict(),
        ignore_order=True,
        verbose_level=2,
    )
    assert diff == {}, "Encounter compare failed"


@pytest.mark.parametrize("input_fixture_name, expected_procedure_fixture_name, expected_encounter_fixture_name",
                         [
                             ("patient_hcpcs_sample",
                              "expected_procedure_hcpcs",
                              "expected_encounter_hcpcs"),
                             ("patient_hcpcs_sample_no_modifier_system",
                              "expected_procedure_hcpcs_no_modifier_system",
                              "expected_encounter_hcpcs")
                         ], )
def test_hcpcs_procedure(
    request,
    input_fixture_name,
    expected_procedure_fixture_name,
    expected_encounter_fixture_name
):
    input_model = request.getfixturevalue(input_fixture_name)
    expected_procedure = request.getfixturevalue(expected_procedure_fixture_name)
    expected_encounter = request.getfixturevalue(expected_encounter_fixture_name)

    group_by_key = input_model.get("accountNumber")
    results: List[Resource] = convert_record(
        group_by_key, input_model, None
    )
    assert results
    assert len(results) == 2, "Unexpected resource count generated"
    enc: Encounter = None
    proc: Procedure = None
    for r in results:
        if r.resource_type == "Encounter":
            enc = r

            assert enc.identifier
            assert len(enc.identifier) == 3, "Encounter: Identifier count is incorrect"
        elif r.resource_type == "Procedure":
            proc = r

            assert proc.identifier
            assert len(proc.identifier) == 3, "Procedure: Identifier count is incorrect"
        else:
            assert False, "Unexpected resource type: " + r.json()

    fhir_procedure: Procedure = Procedure.parse_obj(proc.dict())
    fhir_encounter: Encounter = Encounter.parse_obj(enc.dict())
    expected_procedure = Procedure(**expected_procedure)
    expected_encounter = Encounter(**expected_encounter)

    # setup encounter.reasonReference to have newly created procedure link
    reason_ref: Reference = expected_encounter.reasonReference[0]
    reason_ref.id = fhir_procedure.id
    reason_ref.reference = "Procedure/" + fhir_procedure.id

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_procedure.dict(),
        fhir_procedure.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}, "Procedure compare failed"

    diff = DeepDiff(
        expected_encounter.dict(),
        fhir_encounter.dict(),
        ignore_order=True,
        verbose_level=2,
    )
    assert diff == {}, "Encounter compare failed"


def test_procedure(
    procedure_input,
    procedure_output,
    encounter_output,
):
    group_by_key = procedure_input.get("accountNumber")
    results: List[Resource] = convert_record(group_by_key, procedure_input, None)
    assert results
    assert len(results) == 2, "Unexpected resource count generated"
    enc: Encounter = None
    proc: Procedure = None
    for r in results:
        if r.resource_type == "Encounter":
            enc = r
            assert enc.identifier
            assert len(enc.identifier) == 2, "Encounter: Identifier count is incorrect"
        elif r.resource_type == "Procedure":
            proc = r
            assert proc.identifier
            assert len(proc.identifier) == 2, "Procedure: Identifier count is incorrect"
        else:
            assert False, "Unexpected resource type: " + r.json()

    fhir_procedure: Procedure = Procedure.parse_obj(proc.dict())
    fhir_encounter: Encounter = Encounter.parse_obj(enc.dict())
    expected_procedure = Procedure(**procedure_output)
    expected_encounter = Encounter(**encounter_output)

    # setup encounter.reasonReference to have newly created procedure link
    reason_ref: Reference = expected_encounter.reasonReference[0]
    reason_ref.id = fhir_procedure.id
    reason_ref.reference = "Procedure/" + fhir_procedure.id

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_procedure.dict(),
        fhir_procedure.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}, "Procedure compare failed"

    diff = DeepDiff(
        expected_encounter.dict(),
        fhir_encounter.dict(),
        ignore_order=True,
        verbose_level=2,
    )
    assert diff == {}, "Encounter compare failed"
