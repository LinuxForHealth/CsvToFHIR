from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter
from fhir.resources.patient import Patient

from linuxforhealth.csvtofhir.fhirrs.condition import \
    convert_record as convert_record_condition
from linuxforhealth.csvtofhir.model.csv.condition import (DEFAULT_CONDITION_CODE_SYSTEM,
                                                          DEFAULT_CONDITION_SEVERITY_SYSTEM)


@pytest.fixture
def expected_condition_basic_no_encounter():
    return {
        "resourceType": "Condition",
        "id": "basic.resource.id",
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "sample.condition.code-SNOMED"
            },
            {
                "id": "PI.1-1.12345641",
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
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            },
            {
                "id": "RI.basic.resource.id",
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
                "system": "http://example.org",
                "value": "basic.resource.id"
            },
        ],
        "severity": {
            "coding": [
                {"system": DEFAULT_CONDITION_SEVERITY_SYSTEM, "code": "severity.code"}
            ],
            "text": "very severe"
        },
        "code": {
            "coding": [
                {
                    "system": DEFAULT_CONDITION_CODE_SYSTEM,
                    "code": "sample.condition.code"
                }
            ],
            "text": "sample conditionCodeText"
        },
        "subject": {"reference": "Patient/1-1.12345641"},
        "recordedDate": "2021-10-11T20:53:00+00:00"
    }


@pytest.fixture
def expected_patient_any():
    return {
        "resourceType": "Patient",
        "id": "1-1.12345641",
        "identifier": [
            {
                "id": "PI.1-1.12345641",
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
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            }
        ]
    }


@pytest.fixture
def expected_condition_encounter_diagnosis():
    return {
        "resourceType": "Condition",
        "id": "basic.resource.id",
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "sample.condition.code-SNOMED"
            },
            {
                "id": "PI.1-1.12345641",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "PI",
                            "display": "Patient internal identifier",
                        }
                    ],
                    "text": "Patient internal identifier",
                },
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "http://example.org",
                "value": "ENC.123"
            },
            {
                "id": "RI.basic.resource.id",
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
                "system": "http://example.org",
                "value": "basic.resource.id"
            },
        ],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }
                ],
                "text": "Encounter Diagnosis"
            }
        ],
        "severity": {
            "coding": [
                {"system": DEFAULT_CONDITION_SEVERITY_SYSTEM, "code": "severity.code"}
            ],
            "text": "very severe"
        },
        "code": {
            "coding": [
                {
                    "system": DEFAULT_CONDITION_CODE_SYSTEM,
                    "code": "sample.condition.code"
                }
            ],
            "text": "sample conditionCodeText"
        },
        "subject": {"reference": "Patient/1-1.12345641"},
        "encounter": {"reference": "Encounter/encounter-123"},
        "recordedDate": "2021-10-12T20:53:00+00:00",
        "onsetDateTime": "2021-10-11T20:53:00+00:00",
        "abatementDateTime": "2021-12-11T20:53:00+00:00",
        "clinicalStatus": {
            "coding": [
                {
                    "code": "active",
                    "display": "Active",
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical"
                }
            ],
            "text": "Active",
        },
        "verificationStatus": {
            "coding": [
                {
                    "code": "entered-in-error",
                    "display": "Entered in Error",
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status"
                }
            ],
            "text": "Entered in Error",
        }
    }


@pytest.fixture
def expected_encounter_encounter_diagnosis():
    return {
        "resourceType": "Encounter",
        "id": "encounter-123",
        "identifier": [
            {
                "id": "PI.1-1.12345641",
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
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "http://example.org",
                "value": "ENC.123"
            },
            {
                "id": "RI.encounter-123",
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
                "system": "http://example.org",
                "value": "encounter_123"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/1-1.12345641"},
        "diagnosis": [
            {
                "id": "1",
                "condition": {
                    "reference": "Condition/basic.resource.id",
                    "display": "sample.condition.code (sample conditionCodeText)"
                },
                "rank": 1
            }
        ],
        "extension": [
            {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/claim-type",
                "valueString": "PROFESSIONAL"
            }
        ],
    }


@pytest.fixture
def expected_condition_encounter_diagnosis2():
    return {
        "resourceType": "Condition",
        "id": "basic.resource.id",
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "ABC123-clientcode"
            },
            {
                "id": "PI.112233",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "PI",
                            "display": "Patient internal identifier",
                        }
                    ],
                    "text": "Patient internal identifier",
                },
                "system": "urn:id:client",
                "value": "112233"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "urn:id:client",
                "value": "ENC.123"
            },
            {
                "id": "RI.basic.resource.id",
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
                "system": "urn:id:client",
                "value": "basic.resource.id"
            },
        ],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }
                ],
                "text": "Encounter Diagnosis"
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "urn:id:clientcode",
                    "code": "ABC123"
                }
            ]
        },
        "subject": {"reference": "Patient/112233"},
        "encounter": {"reference": "Encounter/encounter-123"}
    }


@pytest.fixture
def expected_encounter_encounter_diagnosis2():
    return {
        "resourceType": "Encounter",
        "id": "encounter-123",
        "identifier": [
            {
                "id": "PI.112233",
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
                "system": "urn:id:client",
                "value": "112233"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "urn:id:client",
                "value": "ENC.123"
            },
            {
                "id": "RI.encounter-123",
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
                "system": "urn:id:client",
                "value": "encounter_123"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/112233"},
        "diagnosis": [
            {
                "id": "1",
                "condition": {
                    "reference": "Condition/basic.resource.id",
                    "display": "ABC123"
                },
                "use": {
                    "coding": [
                        {
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/wh-diagnosis-use-type",
                            "code": "billing",
                            "display": "Billing"
                        }
                    ],
                    "text": "Billing"
                },
                "rank": 1
            }
        ]
    }


@pytest.fixture
def expected_encounter_encounter_diagnosis3():
    return {
        "resourceType": "Encounter",
        "id": "encounter-123",
        "identifier": [
            {
                "id": "PI.112233",
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
                "system": "urn:id:client",
                "value": "112233"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "urn:id:client",
                "value": "ENC.123"
            },
            {
                "id": "RI.encounter-123",
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
                "system": "urn:id:client",
                "value": "encounter_123"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/112233"},
        "diagnosis": [
            {
                "id": "ABC123",
                "condition": {
                    "reference": "Condition/basic.resource.id",
                    "display": "ABC123"
                },
                "use": {
                    "coding": [
                        {
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/wh-diagnosis-use-type",
                            "code": "AD",
                            "display": "Admission diagnosis"
                        }
                    ],
                    "text": "Admission diagnosis"
                }
            }
        ]
    }


@pytest.fixture
def expected_condition_problem_list():
    return {
        "resourceType": "Condition",
        "id": "basic.resource.id",
        "extension": [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/condition-diseaseCourse",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "code": "90734009",
                            "display": "Chronic (qualifier value)",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "chronic"
                }
            }
        ],
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "sample.condition.code-SNOMED"
            },
            {
                "id": "PI.1-1.12345641",
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
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "http://example.org",
                "value": "ENC.123"
            },
            {
                "id": "RI.basic.resource.id",
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
                "system": "http://example.org",
                "value": "basic.resource.id"
            },
        ],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "problem-list-item",
                        "display": "Problem List Item"
                    }
                ],
                "text": "Problem List Item"
            }
        ],
        "severity": {
            "coding": [
                {"system": DEFAULT_CONDITION_SEVERITY_SYSTEM, "code": "severity.code"}
            ],
            "text": "very severe"
        },
        "code": {
            "coding": [
                {
                    "system": DEFAULT_CONDITION_CODE_SYSTEM,
                    "code": "sample.condition.code"
                }
            ],
            "text": "sample conditionCodeText",
        },
        "recordedDate": "2021-10-11T20:53:00+00:00",
        "subject": {"reference": "Patient/1-1.12345641"},
        "encounter": {"reference": "Encounter/encounter-123"}
    }


@pytest.fixture
def expected_encounter_problem_list():
    return {
        "resourceType": "Encounter",
        "id": "encounter-123",
        "identifier": [
            {
                "id": "PI.1-1.12345641",
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
                "system": "http://example.org",
                "value": "1-1.12345641"
            },
            {
                "id": "MR.mrn1234567",
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
                "system": "http://example.org",
                "value": "mrn1234567"
            },
            {
                "id": "AN.basic.account.number",
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
                "system": "http://example.org",
                "value": "basic.account.number"
            },
            {
                "id": "VN.ENC.123",
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
                "system": "http://example.org",
                "value": "ENC.123"
            },
            {
                "id": "RI.encounter-123",
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
                "system": "http://example.org",
                "value": "encounter_123"
            },
        ],
        "status": "unknown",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "temp-unknown",
            "display": "Temporarily Unknown"
        },
        "subject": {"reference": "Patient/1-1.12345641"},
        "reasonReference": [
            {
                "id": "Condition-basic.resource.id",
                "reference": "Condition/basic.resource.id",
                "display": "sample.condition.code (sample conditionCodeText)"
            }
        ]
    }


@pytest.fixture
def condition_record_basic_no_encounter():
    return {
        "patientInternalId": "1-1.12345641",
        "accountNumber": "basic.account.number",
        "mrn": "mrn1234567",
        # no "encounterInternalId"
        # no "encounterNumber"
        "resourceInternalId": "basic.resource.id",
        "assigningAuthority": "http://example.org",
        # no "conditionCategory"
        # no "conditionDiagnosisRank"
        "conditionRecordedDateTime": "2021-10-11T20:53:00.000Z",
        "conditionCode": "sample.condition.code",
        "conditionCodeSystem": DEFAULT_CONDITION_CODE_SYSTEM,
        "conditionCodeText": "sample conditionCodeText",
        "conditionSeverityCode": "severity.code",
        "conditionSeveritySystem": DEFAULT_CONDITION_SEVERITY_SYSTEM,
        "conditionSeverityText": "very severe",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def condition_record_encounter_diagnosis():
    return {
        "patientInternalId": "1-1.12345641",
        "accountNumber": "basic.account.number",
        "mrn": "mrn1234567",
        "encounterInternalId": "encounter_123",
        "encounterNumber": "ENC.123",
        "resourceInternalId": "basic.resource.id",
        "assigningAuthority": "http://example.org",
        "conditionCategory": "encounter-diagnosis",
        "conditionDiagnosisRank": "1",
        "conditionRecordedDateTime": "2021-10-12T20:53:00.000Z",
        "conditionOnsetDateTime": "2021-10-11T20:53:00.000Z",
        "conditionAbatementDateTime": "2021-12-11T20:53:00.000Z",
        "conditionCode": "sample.condition.code",
        "conditionCodeSystem": DEFAULT_CONDITION_CODE_SYSTEM,
        "conditionCodeText": "sample conditionCodeText",
        "conditionSeverityCode": "severity.code",
        "conditionSeveritySystem": DEFAULT_CONDITION_SEVERITY_SYSTEM,
        "conditionSeverityText": "very severe",
        # no use or rank
        "conditionClinicalStatus": "active",
        "conditionVerificationStatus": "entered-in-error",
        "encounterClaimType": "PROFESSIONAL",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def condition_record_encounter_diagnosis2():
    # Tests different values for diagnosis role and principal diagnosis
    return {
        "patientInternalId": "112233",
        "encounterInternalId": "encounter_123",
        "encounterNumber": "ENC.123",
        "resourceInternalId": "basic.resource.id",
        "assigningAuthority": "urn:id:client",
        "conditionCategory": "encounter-diagnosis",
        "conditionCode": "ABC123",
        "conditionCodeSystem": "urn:id:clientcode",
        "conditionDiagnosisUse": "billing",  # both use...
        "conditionDiagnosisRank": 1,         # ... and rank.
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def condition_record_encounter_diagnosis3():
    # Tests different values for diagnosis role and principal diagnosis
    return {
        "patientInternalId": "112233",
        "encounterInternalId": "encounter_123",
        "encounterNumber": "ENC.123",
        "resourceInternalId": "basic.resource.id",
        "assigningAuthority": "urn:id:client",
        "conditionCategory": "encounter-diagnosis",
        "conditionCode": "ABC123",
        "conditionCodeSystem": "urn:id:clientcode",
        "conditionDiagnosisUse": "AD",  # use only
        # no rank
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def condition_record_problem_list():
    return {
        "patientInternalId": "1-1.12345641",
        "accountNumber": "basic.account.number",
        "mrn": "mrn1234567",
        "encounterInternalId": "encounter_123",
        "encounterNumber": "ENC.123",
        "resourceInternalId": "basic.resource.id",
        "assigningAuthority": "http://example.org",
        "conditionCategory": "problem-list-item",
        "conditionDiagnosisRank": "1",
        "conditionRecordedDateTime": "2021-10-11T20:53:00.000Z",
        "conditionCode": "sample.condition.code",
        "conditionCodeSystem": DEFAULT_CONDITION_CODE_SYSTEM,
        "conditionCodeText": "sample conditionCodeText",
        "conditionSeverityCode": "severity.code",
        "conditionSeveritySystem": DEFAULT_CONDITION_SEVERITY_SYSTEM,
        "conditionSeverityText": "very severe",
        "conditionChronicity": "chronic",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


def test_convert_condition_simple_no_encounter(
    condition_record_basic_no_encounter, expected_condition_basic_no_encounter
):
    result_data: List = convert_record_condition(
        "", condition_record_basic_no_encounter
    )

    assert len(result_data) == 1
    try:
        # loading into fhir.resource test validity of the object
        fhir_record: Condition = Condition.parse_obj(result_data[0].dict())
    except Exception:
        assert False, "Invalid Condition resource created"

    assert fhir_record.resource_type == "Condition"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 5  # PI, MR, AN, RI,extID
    expected_resource = Condition(**expected_condition_basic_no_encounter)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff


def test_convert_condition_encounter_diagnosis(
    condition_record_encounter_diagnosis,
    expected_patient_any,
    expected_condition_encounter_diagnosis,
    expected_encounter_encounter_diagnosis
):
    result_data: List = convert_record_condition(
        "", condition_record_encounter_diagnosis
    )

    assert len(result_data) == 3  # Patient, Encounter, and Condition
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_patient: Patient = Patient.parse_obj(result_data[0].dict())
        fhir_record_encounter: Encounter = Encounter.parse_obj(result_data[1].dict())
        fhir_record_condition: Condition = Condition.parse_obj(result_data[2].dict())
    except Exception:
        assert False, "Invalid Patient, Encounter, or Condition resource created"
    assert fhir_record_patient.resource_type == "Patient"
    assert fhir_record_condition.resource_type == "Condition"
    assert fhir_record_encounter.resource_type == "Encounter"
    assert fhir_record_patient.identifier
    assert fhir_record_condition.identifier
    assert fhir_record_encounter.identifier
    assert len(fhir_record_patient.identifier) == 3  # PI, MR, AN
    assert len(fhir_record_condition.identifier) == 6  # PI, MR, AN, RI, extID, VN
    assert len(fhir_record_encounter.identifier) == 5  # PI, MR, AN, RI, VN

    expected_resource_patient = Patient(**expected_patient_any)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_patient.dict(),
        fhir_record_patient.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_condition = Condition(**expected_condition_encounter_diagnosis)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_condition.dict(),
        fhir_record_condition.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_encounter = Encounter(**expected_encounter_encounter_diagnosis)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_encounter.dict(),
        fhir_record_encounter.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
        ignore_order=True
    ).pretty()
    assert diff == "", diff


def test_convert_condition_encounter_diagnosis2(
    condition_record_encounter_diagnosis2,
    expected_condition_encounter_diagnosis2,
    expected_encounter_encounter_diagnosis2
):
    result_data: List = convert_record_condition(
        "", condition_record_encounter_diagnosis2
    )

    assert len(result_data) == 2  # Encounter, Condition
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_encounter: Encounter = Encounter.parse_obj(result_data[0].dict())
    except Exception:
        assert False, "Invalid Encounter resource created"
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_condition: Condition = Condition.parse_obj(result_data[1].dict())
    except Exception:
        assert False, "Invalid  Condition resource created"
    assert fhir_record_condition.resource_type == "Condition"
    assert fhir_record_encounter.resource_type == "Encounter"
    assert fhir_record_condition.identifier
    assert fhir_record_encounter.identifier
    assert len(fhir_record_condition.identifier) == 4  # PI, RI, extID, VN
    assert len(fhir_record_encounter.identifier) == 3  # PI, RI, VN
    assert len(fhir_record_encounter.diagnosis) == 1   # Billing

    expected_resource_condition = Condition(**expected_condition_encounter_diagnosis2)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_condition.dict(),
        fhir_record_condition.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_encounter = Encounter(**expected_encounter_encounter_diagnosis2)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_encounter.dict(),
        fhir_record_encounter.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
        ignore_order=True
    ).pretty()
    assert diff == "", diff


# similar to test_convert_condition_encounter_diagnosis2, except conditionDiagnosisUse has no
# conditionDiagnosisRank
def test_convert_condition_encounter_diagnosis3(
    condition_record_encounter_diagnosis3,
    expected_condition_encounter_diagnosis2,  # Same condition as test_convert_condition_encounter_diagnosis2
    expected_encounter_encounter_diagnosis3
):
    result_data: List = convert_record_condition(
        "", condition_record_encounter_diagnosis3
    )

    assert len(result_data) == 2  # Encounter, Condition
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_encounter: Encounter = Encounter.parse_obj(result_data[0].dict())
    except Exception:
        assert False, "Invalid Encounter resource created"
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_condition: Condition = Condition.parse_obj(result_data[1].dict())
    except Exception:
        assert False, "Invalid  Condition resource created"
    assert fhir_record_condition.resource_type == "Condition"
    assert fhir_record_encounter.resource_type == "Encounter"
    assert fhir_record_condition.identifier
    assert fhir_record_encounter.identifier
    assert len(fhir_record_condition.identifier) == 4  # PI, RI, extID, VN
    assert len(fhir_record_encounter.identifier) == 3  # PI, RI, VN
    assert len(fhir_record_encounter.diagnosis) == 1   # AD

    expected_resource_condition = Condition(**expected_condition_encounter_diagnosis2)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_condition.dict(),
        fhir_record_condition.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_encounter = Encounter(**expected_encounter_encounter_diagnosis3)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_encounter.dict(),
        fhir_record_encounter.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
        ignore_order=True
    ).pretty()
    assert diff == "", diff


def test_convert_condition_encounter_status(
    condition_record_encounter_diagnosis,
    expected_patient_any,
    expected_condition_encounter_diagnosis,
    expected_encounter_encounter_diagnosis
):
    condition_record_encounter_diagnosis["encounterStatus"] = "planned"
    result_data: List = convert_record_condition(
        "", condition_record_encounter_diagnosis
    )

    assert len(result_data) == 3  # Patient, Encounter, and Condition
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_patient: Patient = Patient.parse_obj(result_data[0].dict())
        fhir_record_encounter: Encounter = Encounter.parse_obj(result_data[1].dict())
        fhir_record_condition: Condition = Condition.parse_obj(result_data[2].dict())
    except Exception:
        assert False, "Invalid Patient, Encounter, or Condition resource created"
    assert fhir_record_patient.resource_type == "Patient"
    assert fhir_record_condition.resource_type == "Condition"
    assert fhir_record_encounter.resource_type == "Encounter"
    assert fhir_record_patient.identifier
    assert fhir_record_condition.identifier
    assert fhir_record_encounter.identifier
    assert len(fhir_record_patient.identifier) == 3  # PI, MR, AN
    assert len(fhir_record_condition.identifier) == 6  # PI, MR, AN, RI, extID, VN
    assert len(fhir_record_encounter.identifier) == 5  # PI, MR, AN, RI, VN

    expected_resource_patient = Patient(**expected_patient_any)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_patient.dict(),
        fhir_record_patient.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_condition = Condition(**expected_condition_encounter_diagnosis)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_condition.dict(),
        fhir_record_condition.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_encounter: Encounter = Encounter(**expected_encounter_encounter_diagnosis)
    expected_resource_encounter.status = "planned"
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_encounter.dict(),
        fhir_record_encounter.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff


def test_convert_condition_problem_list(
    condition_record_problem_list,
    expected_patient_any,
    expected_condition_problem_list,
    expected_encounter_problem_list
):
    result_data: List = convert_record_condition("", condition_record_problem_list)

    assert len(result_data) == 3  # Patient, Encounter, and Condition
    try:
        # loading into fhir.resource test validity of the object
        fhir_record_patient: Patient = Patient.parse_obj(result_data[0].dict())
        fhir_record_encounter: Encounter = Encounter.parse_obj(result_data[1].dict())
        fhir_record_condition: Condition = Condition.parse_obj(result_data[2].dict())
    except Exception:
        assert False, "Invalid Patient, Encounter, or Condition resource created"
    assert fhir_record_patient.resource_type == "Patient"
    assert fhir_record_condition.resource_type == "Condition"
    assert fhir_record_encounter.resource_type == "Encounter"
    assert fhir_record_patient.identifier
    assert fhir_record_condition.identifier
    assert fhir_record_encounter.identifier
    assert len(fhir_record_patient.identifier) == 3  # PI, MR, AN
    assert len(fhir_record_condition.identifier) == 6  # PI, MR, AN, RI, extID, VN
    assert len(fhir_record_encounter.identifier) == 5  # PI, MR, AN, RI, VN

    expected_resource_patient = Patient(**expected_patient_any)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_patient.dict(),
        fhir_record_patient.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource = Condition(**expected_condition_problem_list)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record_condition.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff

    expected_resource_encounter = Encounter(**expected_encounter_problem_list)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource_encounter.dict(),
        fhir_record_encounter.dict(),
        verbose_level=2,
        exclude_regex_paths=exclude_regex
    ).pretty()
    assert diff == "", diff
