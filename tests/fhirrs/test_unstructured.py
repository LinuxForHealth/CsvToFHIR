from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.practitioner import Practitioner
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs.diagnostic_report import \
    convert_record as convert_record_diag_report
from linuxforhealth.csvtofhir.fhirrs.document_reference import \
    convert_record as convert_record_doc_reference
from linuxforhealth.csvtofhir.fhirrs.unstructured import \
    convert_record as convert_record_unstructured
from linuxforhealth.csvtofhir.model.csv.unstructured import DOCUMENT_TYPE_CODING_SYSTEM

# Used to prove that ContentType can be overridden


@pytest.fixture
def unstructured_docref_with_detailed_content_type():
    return {
        "resourceType": "DocumentReference",
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "encounterInternalId": "111_E1111",
        "resourceStatus": None,
        "documentStatus": "final",
        "documentTypeCode": "11506-3",
        "documentTypeCodeText": "Progress note",
        "documentDateTime": "2021-11-04T09:18:00.000Z",
        "documentAttachmentContentType": "text/plain;charset=UTF-8",
        "documentAttachmentContent": "Making good progress. Meeting again in 2 weeks",
        "documentAttachmentTitle": "Progress Note",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


# Used to show that ContentType is defaulted when missing.
# Also tests documentType defaults.
@pytest.fixture
def unstructured_docref_missing_content_type():
    return {
        "resourceType": "DocumentReference",
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "encounterInternalId": "111_E1111",
        "resourceStatus": None,
        "documentStatus": "final",
        # "documentTypeCode"  purposely not specified to test default
        # "documentTypeCodeText"    purposely not specified to test default
        "documentDateTime": "2021-11-04T09:18:00.000Z",
        # "documentAttachmentContentType"  purposely missing to test default is activated
        "documentAttachmentContent": "Making good progress. Meeting again in 2 weeks",
        "documentAttachmentTitle": "Progress Note",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def unstructured_diagrpt():
    return {
        "resourceType": "DiagnosticReport",
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "encounterInternalId": "111_E1111",
        "documentStatus": "final",
        "documentDateTime": "2021-11-04T09:18:00.000Z",
        "documentAttachmentContent": "Making good progress. Meeting again in 2 weeks",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def unstructured_docref_w_practitioner():
    return {
        "assigningAuthority": "111",
        "accountNumber": "111_E1111",
        "encounterInternalId": "111_E1111",
        "resourceStatus": "current",
        "documentStatus": "preliminary",
        "documentDateTime": "2021-11-04T09:18:00.000Z",
        "documentAttachmentContentType": "text/plain",
        "documentAttachmentContent": "Making good progress. Meeting again in 2 weeks",
        "documentAttachmentTitle": "Progress Note",
        "practitionerNameLast": "GOOD",
        "practitionerNameFirst": "JOSEPH",
        "practitionerNPI": "N2513N2513N",
        "practitionerInternalId": "OBMOATZ",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


@pytest.fixture
def expected_output_docref_with_detailed_content_type():
    return {
        "resourceType": "DocumentReference",
        "id": "uuid",
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
                "id": "extID",
                "system": "urn:id:extID",
                "value": "11506-3-2021-11-04T09:18:00+00:00"
            }
        ],
        "status": "current",
        "docStatus": "final",
        "type": {
            "coding": [
                {
                    "system": DOCUMENT_TYPE_CODING_SYSTEM,
                    "code": "11506-3",
                    "display": "Progress note"
                },
            ],
            "text": "Progress note"
        },
        "subject": {"reference": "Patient/111-E1111"},
        "date": "2021-11-04T09:18:00+00:00",
        "context": {"encounter": [{"reference": "Encounter/111-E1111"}]},
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain;charset=UTF-8",
                    "data": "TWFraW5nIGdvb2QgcHJvZ3Jlc3MuIE1lZXRpbmcgYWdhaW4gaW4gMiB3ZWVrcw==",
                    "creation": "2021-11-04T09:18:00+00:00",
                    "title": "Progress Note"
                }
            }
        ]
    }


@pytest.fixture
def expected_output_docref_for_missing_content_type():
    return {
        "resourceType": "DocumentReference",
        "id": "uuid",
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
                "id": "extID",
                "system": "urn:id:extID",
                "value": "67781-5-2021-11-04T09:18:00+00:00"
            }
        ],
        "status": "current",
        "docStatus": "final",
        "type": {
            "coding": [
                {
                    "system": DOCUMENT_TYPE_CODING_SYSTEM,
                    "code": "67781-5",
                    "display": "Summarization of encounter note Narrative"
                }
            ],
            "text": "Summarization of encounter note Narrative"
        },
        "subject": {"reference": "Patient/111-E1111"},
        "date": "2021-11-04T09:18:00+00:00",
        "context": {"encounter": [{"reference": "Encounter/111-E1111"}]},
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "data": "TWFraW5nIGdvb2QgcHJvZ3Jlc3MuIE1lZXRpbmcgYWdhaW4gaW4gMiB3ZWVrcw==",
                    "creation": "2021-11-04T09:18:00+00:00",
                    "title": "Progress Note"
                }
            }
        ]
    }


@pytest.fixture
def expected_output_diagrpt():
    return {
        "resourceType": "DiagnosticReport",
        "id": "uuid",
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
                "id": "extID",
                "system": "urn:id:extID",
                "value": "50398-7-2021-11-04T09:18:00+00:00"
            }
        ],
        "encounter": {"reference": "Encounter/111-E1111"},
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": DOCUMENT_TYPE_CODING_SYSTEM,
                    "code": "50398-7",
                    "display": "Narrative diagnostic report [Interpretation]"
                }
            ],
            "text": "Narrative diagnostic report [Interpretation]"
        },
        "subject": {"reference": "Patient/111-E1111"},
        "issued": "2021-11-04T09:18:00+00:00",
        "presentedForm": [
            {
                "contentType": "text/plain",
                "data": "TWFraW5nIGdvb2QgcHJvZ3Jlc3MuIE1lZXRpbmcgYWdhaW4gaW4gMiB3ZWVrcw==",
                "creation": "2021-11-04T09:18:00+00:00"
            }
        ]
    }


@pytest.fixture
def expected_output_docref_w_pratitioner():
    return {
        "resourceType": "DocumentReference",
        "id": "uuid",
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
                "id": "extID",
                "system": "urn:id:extID",
                "value": "67781-5-2021-11-04T09:18:00+00:00"
            }
        ],
        "status": "current",
        "docStatus": "preliminary",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "67781-5",
                    "display": "Summarization of encounter note Narrative"
                }
            ],
            "text": "Summarization of encounter note Narrative"
        },
        "subject": {"reference": "Patient/111-E1111"},
        "date": "2021-11-04T09:18:00+00:00",
        "author": [{"reference": "Practitioner/OBMOATZ", "display": "JOSEPH GOOD"}],
        "context": {"encounter": [{"reference": "Encounter/111-E1111"}]},
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "data": "TWFraW5nIGdvb2QgcHJvZ3Jlc3MuIE1lZXRpbmcgYWdhaW4gaW4gMiB3ZWVrcw==",
                    "title": "Progress Note",
                    "creation": "2021-11-04T09:18:00+00:00"
                }
            }
        ]
    }


@pytest.fixture
def expected_practitioner_resource():
    return {
        "resourceType": "Practitioner",
        "id": "OBMOATZ",
        "identifier": [
            {
                "id": "RI.OBMOATZ",
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
                "value": "OBMOATZ"
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
                "value": "N2513N2513N"
            }
        ],
        "name": [{
            "text": "JOSEPH GOOD",
            "family": "GOOD",
            "given": ["JOSEPH"]
        }]
    }


# Prove that ContentType can be overridden
def test_convert_record_unstructured_docref_w_detailed_content_type(
    unstructured_docref_with_detailed_content_type,
    expected_output_docref_with_detailed_content_type,
):
    group_by_key = unstructured_docref_with_detailed_content_type.get("accountNumber")

    results: List[Resource] = convert_record_unstructured(
        group_by_key, unstructured_docref_with_detailed_content_type, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "DocumentReference", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert (
        len(result.identifier) == 2
    ), "DocumentReference: identifier count is incorrect"
    expected_resource = DocumentReference(
        **expected_output_docref_with_detailed_content_type
    )
    fhir_result: DocumentReference = DocumentReference.parse_obj(result.dict())
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}


# This test confirms that when the unstructuredContentType is missing, it is defaulted
def test_convert_record_unstructured_docref_missing_content_type(
    unstructured_docref_missing_content_type,
    expected_output_docref_for_missing_content_type,
):
    group_by_key = unstructured_docref_missing_content_type.get("accountNumber")

    results: List[Resource] = convert_record_unstructured(
        group_by_key, unstructured_docref_missing_content_type, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "DocumentReference", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert (
        len(result.identifier) == 2
    ), "DocumentReference: identifier count is incorrect"
    expected_resource = DocumentReference(
        **expected_output_docref_for_missing_content_type
    )
    fhir_result: DocumentReference = DocumentReference.parse_obj(result.dict())
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}


def test_convert_record_unstructured_w_practitioner(
    unstructured_docref_w_practitioner,
    expected_output_docref_w_pratitioner,
    expected_practitioner_resource,
):
    group_by_key = unstructured_docref_w_practitioner.get("accountNumber")

    results: List[Resource] = convert_record_unstructured(
        group_by_key, unstructured_docref_w_practitioner, None
    )

    assert len(results) == 2, "Unexpected resource count generated"
    expected_resource_list = ["DocumentReference", "Practitioner"]
    result: Resource

    for result in results:
        rs_type = result.resource_type
        if rs_type not in expected_resource_list:
            assert False, f"Unexpected Resource Type: {rs_type}"
        expected_resource_list.remove(rs_type)

        if rs_type == "DocumentReference":
            assert (
                len(result.identifier) == 2
            ), "Encounter: identifier count is incorrect"
            expected_resource = DocumentReference(
                **expected_output_docref_w_pratitioner
            )
            fhir_result: DocumentReference = DocumentReference.parse_obj(
                result.dict()
            )
        elif rs_type == "Practitioner":
            assert (
                len(result.identifier) == 2
            ), "Location: identifier count is incorrect"
            expected_resource = Practitioner(**expected_practitioner_resource)
            fhir_result: Practitioner = Practitioner.parse_obj(result.dict())
        else:
            assert False, "Unexpected resource type generated"

        exclude_regex = [r"root\['id'\]"]
        diff = DeepDiff(
            expected_resource.dict(),
            fhir_result.dict(),
            ignore_order=True,
            verbose_level=2,
            exclude_regex_paths=exclude_regex,
        )
        assert diff == {}
    assert len(expected_resource_list) == 0, (
        "Missing Resources: " + expected_resource_list
    )


def test_convert_record_diagnostic_report(
    unstructured_diagrpt, expected_output_diagrpt
):
    group_by_key = unstructured_diagrpt.get("accountNumber")
    results: List[Resource] = convert_record_diag_report(
        group_by_key, unstructured_diagrpt, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]
    assert result.resource_type == "DiagnosticReport", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert (
        len(result.identifier) == 2
    ), "DiagnosticReport: identifier count is incorrect"

    fhir_result: DiagnosticReport = DiagnosticReport.parse_obj(result.dict())

    expected_resource = DiagnosticReport(**expected_output_diagrpt)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}


def test_convert_record_document_reference(
    unstructured_docref_missing_content_type,
    expected_output_docref_for_missing_content_type,
):
    group_by_key = unstructured_docref_missing_content_type.get("accountNumber")

    results: List[Resource] = convert_record_doc_reference(
        group_by_key, unstructured_docref_missing_content_type, None
    )
    assert len(results) == 1, "Unexpected resource count generated"
    result: Resource = results[0]

    assert result.resource_type == "DocumentReference", (
        "Unexpected Resource Type: " + result.resource_type
    )
    assert result.identifier
    assert (
        len(result.identifier) == 2
    ), "DocumentReference: identifier count is incorrect"
    expected_resource = DocumentReference(
        **expected_output_docref_for_missing_content_type
    )
    fhir_result: DocumentReference = DocumentReference.parse_obj(result.dict())
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_result.dict(),
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_regex,
    )
    assert diff == {}
