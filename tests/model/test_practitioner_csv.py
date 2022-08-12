

import pytest

from linuxforhealth.csvtofhir.model.csv.practitioner import PractitionerCsv


@pytest.fixture
def practitioner_dict():
    return {
        "resourceInternalId": "ABCDEF",
        "identifier_practitionerNPI": "N1234567890"
    }


@pytest.fixture
def practitioner_alias():
    return {
        "practitionerInternalId": "ABCDEF",
        "practitionerNPI": "N1234567890",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }


def test_practitioner_alias(practitioner_alias):
    pr: PractitionerCsv = PractitionerCsv.parse_obj(practitioner_alias)
    assert pr.identifier_practitionerNPI == "N1234567890"
    assert pr.resourceInternalId == "ABCDEF"
