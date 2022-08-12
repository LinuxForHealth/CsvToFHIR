
# Test SSN removal of invalid values
import json

import pytest
from deepdiff import DeepDiff

from linuxforhealth.csvtofhir.model.csv import unstructured

CC_DIAG_REPORT_CODE = {
    "coding": [
        {
            "system": unstructured.DOCUMENT_TYPE_CODING_SYSTEM,
            "code": "50398-7",
            "display": "Narrative diagnostic report [Interpretation]"
        }
    ],
    "text": "Narrative diagnostic report [Interpretation]"
}
CC_DOC_REF_CODE = {
    "coding": [
        {
            "system": unstructured.DOCUMENT_TYPE_CODING_SYSTEM,
            "code": "67781-5",
            "display": "Summarization of encounter note Narrative"
        }
    ],
    "text": "Summarization of encounter note Narrative"
}


@pytest.mark.parametrize(
    "resource_type, expected_resource_type, expected_cc",
    [
        (None, "DocumentReference", CC_DOC_REF_CODE),
        ("DocumentReference", "DocumentReference", CC_DOC_REF_CODE),
        ("some other thing", "DocumentReference", CC_DOC_REF_CODE),
        ("DiagnosticReport", "DiagnosticReport", CC_DIAG_REPORT_CODE)
    ]
)
def test_default_document_code(resource_type, expected_resource_type, expected_cc):

    dictionary = {
        "resourceType": resource_type,
        "filePath": "/home/csv/input.csv",
        "rowNum": 0

    }
    document: unstructured.UnstructuredCsv = unstructured.UnstructuredCsv.parse_obj(
        dictionary
    )
    assert document.resourceType == expected_resource_type
    actual_cc = unstructured.get_default_document_code(document.resourceType)
    diff = DeepDiff(expected_cc, json.loads(actual_cc.json()), ignore_order=True)
    assert diff == {}
