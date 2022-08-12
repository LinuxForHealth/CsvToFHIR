import json
from importlib.resources import Resource
from typing import Dict, List

import pytest
from fhir.resources.immunization import Immunization
from fhir.resources.organization import Organization

from linuxforhealth.csvtofhir.fhirrs.immunization import \
    convert_record as immunization_convert_record
from tests.support import deep_diff


@pytest.fixture
def immunization_basic():
    return {
        "patientInternalId": "111_M1111",
        "accountNumber": "111_E1111",
        "mrn": "M1111-1",
        "ssn": "000-00-0000",
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "resourceInternalId": "111_E1111",
        "immunizationDoseQuantity": "0.1",
        "immunizationDoseUnit": "mL",
        "immunizationDoseText": "1.0 ml",
        "encounterInternalId": "ABC1234",
        "encounterNumber": "ABC1234",
        "organizationName": "Sanofi Pasteur",
        "organizationResourceInternalId": "SANPAS",
        "immunizationRouteCode": "372464004",
        "immunizationRouteSystem": "http://snomed.info/sct",
        "immunizationRouteText": "Test String",
        "immunizationSiteCode": "66480008",
        "immunizationSiteSystem": "http://snomed.info/sct",
        "immunizationSiteText": "Test String",
        "immunizationStatus": "not-done",
        "immunizationStatusReasonCode": "MEDPREC",
        "immunizationStatusReasonSystem": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
        "immunizationStatusReasonText": "Test String",
        "immunizationVaccineCode": "8948",
        "immunizationVaccineText": "Purified Protein Derivative of Tuberculin",
        "immunizationVaccineSystem": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "immunizationVaccineCodeList": ["854930^^CVX"],
        "immunizationDate": "2015-11-13 00:00:00",
        "immunizationExpirationDate": "2022-01-01 00:00:00",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@pytest.fixture
def expected_organization_basic():
    return {
        "resourceType": "Organization",
        "id": "SANPAS",
        "identifier": [{
            "id": "RI.SANPAS",
            "type": {
                "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "RI",
                        "display": "Resource identifier"
                }],
                "text": "Resource identifier"
            },
            "value": "SANPAS"
        }],
        "name": "Sanofi Pasteur"
    }


@pytest.fixture
def expected_immunization_basic():
    return {
        "resourceType": "Immunization",
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
                "value": "111_E1111"
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
                "value": "111_E1111"
            },
            {
                "id": "VN.ABC1234",
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
                "value": "ABC1234"
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "854930-CVX"
            }
        ],
        "status": "not-done",
        "statusReason": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                    "code": "MEDPREC",
                    "display": "medical precaution"
                }
            ],
            "text": "Test String"
        },
        "vaccineCode": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "8948"
                }, {
                    "system": "http://hl7.org/fhir/sid/cvx",
                    "code": "854930"
                }
            ],
            "text": "Purified Protein Derivative of Tuberculin"
        },
        "manufacturer": {
            "reference": "Organization/SANPAS",
            "display": "Sanofi Pasteur"
        },
        "patient": {
            "reference": "Patient/111-M1111"
        },
        "encounter": {
            "reference": "Encounter/ABC1234"
        },
        "occurrenceDateTime": "2015-11-13T00:00:00",
        "expirationDate": "2022-01-01",
        "site": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "66480008"
                }
            ],
            "text": "Test String"
        },
        "route": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "372464004"
                }
            ],
            "text": "Test String"
        },
        "doseQuantity": {
            "value": 0.1,
            "unit": "mL"
        }
    }


def test_immunization_basic(
    immunization_basic, expected_immunization_basic, expected_organization_basic
):
    group_by_key = immunization_basic.get("accountNumber")

    results: List[Resource] = immunization_convert_record(
        group_by_key, immunization_basic, None
    )
    assert len(results) == 2, "Unexpected resource count generated"
    result_organization: Resource = results[0]
    result_immunization: Resource = results[1]

    assert result_organization.resource_type == "Organization", (
        "Unexpected Resource Type: " + result_organization.resource_type
    )
    assert result_immunization.resource_type == "Immunization", (
        "Unexpected Resource Type: " + result_immunization.resource_type
    )
    assert result_immunization.identifier
    assert len(result_immunization.identifier) == 6, "Identifier count is incorrect"
    fhir_immunization_result: Immunization = Immunization.parse_obj(result_immunization.dict())
    expected_immunization = Immunization(
        **expected_immunization_basic
    )

    assert result_organization.identifier
    assert len(result_organization.identifier) == 1, "Identifier count is incorrect"
    fhir_organization_result: Organization = Organization.parse_obj(result_organization.dict())
    expected_organization = Organization(
        **expected_organization_basic
    )

    # Flatten and reinflate to json to avoid serialization issues with decimals
    compare_result: Dict = deep_diff(json.loads(expected_immunization.json()),
                                     json.loads(fhir_immunization_result.json()))
    assert compare_result == {}

    compare_result = deep_diff(expected_organization.dict(),
                               fhir_organization_result.dict())
    assert compare_result == {}


def test_immunization_basic_no_date(
    immunization_basic, expected_immunization_basic, expected_organization_basic
):
    """
    Modifies the basic test to see that no date creates an unknown date
    """
    group_by_key = immunization_basic.get("accountNumber")

    # remove the immunizationDate
    del immunization_basic['immunizationDate']

    results: List[Resource] = immunization_convert_record(
        group_by_key, immunization_basic, None
    )
    assert len(results) == 2, "Unexpected resource count generated"
    result_organization: Resource = results[0]
    result_immunization: Resource = results[1]

    assert result_organization.resource_type == "Organization", (
        "Unexpected Resource Type: " + result_organization.resource_type
    )
    assert result_immunization.resource_type == "Immunization", (
        "Unexpected Resource Type: " + result_immunization.resource_type
    )
    assert result_immunization.identifier
    assert len(result_immunization.identifier) == 6, "Identifier count is incorrect"
    fhir_immunization_result: Immunization = Immunization.parse_obj(result_immunization.dict())
    # replace expected occurrenceDateTime with occurrenceString before the test
    del expected_immunization_basic['occurrenceDateTime']
    expected_immunization_basic['occurrenceString'] = "unknown"
    expected_immunization = Immunization(
        **expected_immunization_basic
    )

    assert result_organization.identifier
    assert len(result_organization.identifier) == 1, "Identifier count is incorrect"
    fhir_organization_result: Organization = Organization.parse_obj(result_organization.dict())
    expected_organization = Organization(
        **expected_organization_basic
    )

    # Flatten and reinflate to json to avoid serialization issues with decimals
    compare_result = deep_diff(json.loads(expected_immunization.json()),
                               json.loads(fhir_immunization_result.json()))
    assert compare_result == {}

    compare_result = deep_diff(expected_organization.dict(),
                               fhir_organization_result.dict())
    assert compare_result == {}
