from typing import List

import pytest
from deepdiff import DeepDiff
from fhir.resources.observation import Observation, ObservationReferenceRange
from fhir.resources.practitioner import Practitioner
from fhir.resources.quantity import Quantity
from pydantic.types import Decimal

from linuxforhealth.csvtofhir.fhirrs.observation import convert_record


@pytest.fixture
def expected_observation_practitioner():
    return {
        "resourceType": "Practitioner",
        "id": "TTTTTTR",
        "identifier": [
            {
                "id": "RI.TTTTTTR",
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
                "value": "TTTTTTR"
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
                "value": "N1234567890"
            }
        ]
    }


@pytest.fixture
def expected_observation_height():
    return {
        "resourceType": "Observation",
        "id": "796c935a-93e6-11ec-83f3-8c8590ba7dbd",
        "encounter": {"reference": "Encounter/hospa-ENC1111"},
        "effectiveDateTime": "2022-08-08T10:30:00+00:00",
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "20220808103000-8302-2-LOINC"
            },
            {
                "id": "PI.1-1.12345",
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
                "system": "urn:id:hospa",
                "value": "1-1.12345"
            },
            {
                "id": "AN.hospa-ENC1111",
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
                "value": "hospa_ENC1111"
            },
            {
                "id": "VN.ENC1111",
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
                "value": "ENC1111"
            }
        ],
        "status": "final",
        "subject": {"reference": "Patient/1-1.12345"},
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }
                ],
                "text": "Vital Signs"
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8302-2"
                },
                {
                    "code": "HGT",
                    "system": "urn:id:hospa"
                }
            ],
            "text": "Body height"
        },
        "valueQuantity": {"value": 175.3, "unit": "cm"}
    }


@pytest.fixture
def expected_observation_laboratory():
    return {
        "resourceType": "Observation",
        "id": "e1af309e-93e6-11ec-9c91-8c8590ba7dbd",
        "encounter": {"reference": "Encounter/hospa-ENC1111"},
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "20211011205300-718-7-LOINC"
            },
            {
                "id": "PI.1-1.12345",
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
                "system": "urn:id:hospa",
                "value": "1-1.12345"
            },
            {
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
                "value": "hospa_ENC1111",
                "id": "AN.hospa-ENC1111"
            },
            {
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
                "value": "ENC1111",
                "id": "VN.ENC1111"
            }
        ],
        "subject": {"reference": "Patient/1-1.12345"},
        "status": "unknown",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ],
                "text": "Laboratory"
            }
        ],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "718-7"}],
            "text": "Hemoglobin"
        },
        "effectiveDateTime": "2021-10-11T20:53:00+00:00",
        "performer": [{"reference": "Practitioner/TTTTTTR"}],
        "valueQuantity": {"value": 15.2, "unit": "g/dL"},
        "referenceRange": [{"text": "12.0-16.0"}],
        "interpretation": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "code": "N",
                        "display": "Normal"
                    }
                ],
                "text": "Normal"
            }
        ]
    }


@pytest.fixture
def expected_observation_laboratory_interpretation():
    return {
        "resourceType": "Observation",
        "id": "e1af309e-93e6-11ec-9c91-8c8590ba7dbd",
        "identifier": [
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "20211011205300-718-7-LOINC"
            },
            {
                "id": "PI.1234",
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
                "system": "urn:id:hospa",
                "value": "1234"
            },
        ],
        "subject": {"reference": "Patient/1234"},
        "status": "unknown",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ],
                "text": "Laboratory"
            }
        ],
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "718-7"}],
            "text": "Hemoglobin"
        },
        "effectiveDateTime": "2021-10-11T20:53:00+00:00",
        "valueQuantity": {"value": -1.0, "unit": "g/dL"},
        "referenceRange": [{"text": "12.0-16.0"}],
        "interpretation": [
            {
                "coding": [
                    {
                        "system": "urn:id:tenant",
                        "code": "OS",
                        "display": "Off the scale"
                    }
                ],
                "text": "Off the scale"
            }
        ]
    }


@ pytest.fixture
def observation_height_record_basic():
    return {
        "accountNumber": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "patientInternalId": "1-1.12345",
        "encounterNumber": "ENC1111",
        "encounterInternalId": "hospa_ENC1111",
        "observationCode": "8302-2",
        "observationCodeSystem": "http://loinc.org",
        "observationCodeText": "Body height",
        "observationCodeList": ["HGT^^urn:id:hospa"],
        "observationValue": "175.3",
        "observationValueDataType": "valueQuantity",
        "observationValueUnits": "cm",
        "observationCategory": "vital-signs",
        "observationStatus": "final",
        "observationDateTime": "2022-08-08T10:30:00.000Z",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@ pytest.fixture
def observation_no_test_id():
    return {
        "accountNumber": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "patientInternalId": "1-1.12345",
        "encounterNumber": "ENC1111",
        "encounterInternalId": "hospa_ENC1111",
        "observationCode": None,
        "observationValue": "123",
        "observationValueUnits": "cm",
        "observationCategory": "vital-signs",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@ pytest.fixture
def observation_lab_record_basic():
    return {
        "observationCategory": "laboratory",
        "accountNumber": "hospa_ENC1111",
        "encounterNumber": "ENC1111",
        "encounterInternalId": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "patientInternalId": "1-1.12345",
        "observationCode": "718-7",
        "observationCodeSystem": "http://loinc.org",
        "observationCodeText": "Hemoglobin",
        "observationValue": "15.2",
        "observationValueDataType": "valueQuantity",
        "observationValueUnits": "g/dL",
        "observationRefRangeText": "12.0-16.0",
        "observationDateTime": "2021-10-11T20:53:00.000Z",
        "observationInterpretationCode": "N",
        "practitionerInternalId": "TTTTTTR",
        "practitionerNPI": "N1234567890",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@ pytest.fixture
def observation_lab_record_interpretation():
    return {
        "observationCategory": "laboratory",
        "assigningAuthority": "hospa",
        "patientInternalId": "1234",
        "observationCode": "718-7",
        "observationCodeSystem": "http://loinc.org",
        "observationCodeText": "Hemoglobin",
        "observationValue": "-1",
        "observationValueDataType": "valueQuantity",
        "observationValueUnits": "g/dL",
        "observationRefRangeText": "12.0-16.0",
        "observationDateTime": "2021-10-11T20:53:00.000Z",
        "observationInterpretationCode": "OS",
        "observationInterpretationCodeDisplay": "Off the scale",
        "observationInterpretationCodeSystem": "tenant",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


def test_convert_record_height_simple(
    observation_height_record_basic, expected_observation_height
):
    result_data: List = convert_record("", observation_height_record_basic)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_record: Observation = Observation.parse_obj(result_data[0].dict())

    assert fhir_record.resource_type == "Observation"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 4  # Account Number, SSN and DL, extID
    expected_resource = Observation(**expected_observation_height)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex,
    ).pretty()
    assert diff == "", diff


def test_convert_record_no_test_id(
    observation_no_test_id
):
    result_data: List = convert_record("", observation_no_test_id)

    # A missing value of None should not even create a result
    assert len(result_data) == 0


def test_convert_record_lab_w_practitioner(
    observation_lab_record_basic,
    expected_observation_practitioner,
    expected_observation_laboratory,
):
    result_data: List = convert_record("", observation_lab_record_basic)

    assert len(result_data) == 2
    obj1 = result_data[0].dict()
    obj2 = result_data[1].dict()
    map = {obj1["resourceType"]: obj1, obj2["resourceType"]: obj2}
    assert "Observation" in map.keys()
    assert "Practitioner" in map.keys()

    # loading into fhir.resource test validity of the object
    fhir_obs: Observation = Observation.parse_obj(map["Observation"])

    expected_resource = Observation(**expected_observation_laboratory)

    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_obs.dict(),
        ignore_order=True,
        exclude_regex_paths=exclude_regex,
    ).pretty()
    assert diff == ""

    assert fhir_obs.identifier
    assert len(fhir_obs.identifier) == 4  # Account Number, SSN and DL, extID

    fhir_pr: Practitioner = Practitioner.parse_obj(map["Practitioner"])
    assert fhir_pr.identifier
    assert len(fhir_pr.identifier) == 2  # RI and NPI
    expected_resource = Practitioner(**expected_observation_practitioner)
    diff = DeepDiff(expected_resource, fhir_pr, ignore_order=True)
    assert diff == {}


def test_convert_record_height_simple_2(
    observation_height_record_basic, expected_observation_height
):
    result_data: List = convert_record("", observation_height_record_basic)

    assert len(result_data) == 1
    fhir_record: Observation = Observation.parse_obj(result_data[0].dict())

    assert fhir_record.resource_type == "Observation"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 4  # Account Number, SSN and DL, extID
    expected_resource = Observation(**expected_observation_height)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex,
    ).pretty()
    assert diff == "", diff


def test_convert_record_lab_ref_range(
    observation_lab_record_basic,
    expected_observation_practitioner,
    expected_observation_laboratory,
):
    observation_lab_record_basic["observationRefRange"] = observation_lab_record_basic[
        "observationRefRangeText"
    ]
    result_data: List = convert_record("", observation_lab_record_basic)

    assert len(result_data) == 2
    obj1 = result_data[0].dict()
    obj2 = result_data[1].dict()
    map = {obj1["resourceType"]: obj1, obj2["resourceType"]: obj2}
    assert "Observation" in map.keys()
    # loading into fhir.resource test validity of the object
    fhir_obs: Observation = Observation.parse_obj(map["Observation"])

    expected_resource = Observation(**expected_observation_laboratory)
    expected_ref_range: ObservationReferenceRange = expected_resource.referenceRange[0]
    expected_ref_range.low = Quantity.construct(value=Decimal(12.0), unit="g/dL")
    expected_ref_range.high = Quantity.construct(value=Decimal(16.0), unit="g/dL")

    actual_ref_range: ObservationReferenceRange = fhir_obs.referenceRange[0]
    diff = DeepDiff(
        expected_ref_range.dict(), actual_ref_range.dict(), verbose_level=2
    ).pretty()
    assert diff == "", diff


def test_convert_record_lab_ref_range_text_high_low():
    """
    Text values in ref range low and ref range high, no ref range text provided
    """

    observation_input = {
        "patientInternalId": "1234",
        "observationCode": "test1",
        "observationValue": "Negative",
        "observationRefRangeLow": "Negative",
        "observationRefRangeHigh": "Positive",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }

    result_data: List = convert_record("", observation_input)

    assert len(result_data) == 1
    obj1 = result_data[0].dict()
    assert 'Observation' in obj1.get('resourceType')
    # loading into fhir.resource test validity of the object
    Observation.parse_obj(obj1)

    obs: Observation = result_data[0]
    assert len(obs.referenceRange) == 1

    ref_range: ObservationReferenceRange = obs.referenceRange[0]
    assert ref_range.low is None
    assert ref_range.high is None
    assert ref_range.text == 'low: Negative high: Positive'


def test_convert_record_lab_ref_range_text_provided():
    """
    Text values in ref range low and ref range high and ref range text provided
    """

    observation_input = {
        "patientInternalId": "1234",
        "observationCode": "test1",
        "observationValue": "Negative",
        "observationRefRangeText": "input text",
        "observationRefRangeLow": "Negative",
        "observationRefRangeHigh": "Positive",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }

    result_data: List = convert_record("", observation_input)

    assert len(result_data) == 1
    obj1 = result_data[0].dict()
    assert 'Observation' in obj1.get('resourceType')
    # loading into fhir.resource test validity of the object
    Observation.parse_obj(obj1)

    obs: Observation = result_data[0]
    assert len(obs.referenceRange) == 1

    ref_range: ObservationReferenceRange = obs.referenceRange[0]
    assert ref_range.low is None
    assert ref_range.high is None
    assert ref_range.text == 'input text'


def test_convert_record_lab_ref_range_text_low():
    """
    Text value in ref range low, no ref range high provided, no ref range text provided
    """

    observation_input = {
        "patientInternalId": "1234",
        "observationCode": "test1",
        "observationValue": "Negative",
        "observationRefRangeLow": "Negative",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }

    result_data: List = convert_record("", observation_input)

    assert len(result_data) == 1
    obj1 = result_data[0].dict()
    assert 'Observation' in obj1.get('resourceType')
    # loading into fhir.resource test validity of the object
    Observation.parse_obj(obj1)

    obs: Observation = result_data[0]
    assert len(obs.referenceRange) == 1

    ref_range: ObservationReferenceRange = obs.referenceRange[0]
    assert ref_range.low is None
    assert ref_range.high is None
    assert ref_range.text == 'low: Negative high: None'


def test_convert_record_lab_ref_range_text_high():
    """
    No ref range low provided, text value in ref range high, no ref range text provided
    """

    observation_input = {
        "patientInternalId": "1234",
        "observationCode": "tes1",
        "observationValue": "Negative",
        "observationRefRangeHigh": "Positive",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }
    result_data: List = convert_record("", observation_input)

    assert len(result_data) == 1
    obj1 = result_data[0].dict()
    assert 'Observation' in obj1.get('resourceType')
    # loading into fhir.resource test validity of the object
    Observation.parse_obj(obj1)

    obs: Observation = result_data[0]
    assert len(obs.referenceRange) == 1

    ref_range: ObservationReferenceRange = obs.referenceRange[0]
    assert ref_range.low is None
    assert ref_range.high is None
    assert ref_range.text == 'low: None high: Positive'


def test_convert_record_lab_ref_range_text_mixed():
    """
    Numeric value in ref range low, text value in ref range high, no ref range text provided
    """

    observation_input = {
        "patientInternalId": "1234",
        "observationCode": "test1",
        "observationValue": "Negative",
        "observationRefRangeLow": "1.0",
        "observationRefRangeHigh": "Positive",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }
    result_data: List = convert_record("", observation_input)

    assert len(result_data) == 1
    obj1 = result_data[0].dict()
    assert 'Observation' in obj1.get('resourceType')
    # loading into fhir.resource test validity of the object
    Observation.parse_obj(obj1)

    obs: Observation = result_data[0]
    assert len(obs.referenceRange) == 1

    ref_range: ObservationReferenceRange = obs.referenceRange[0]
    assert ref_range.low.value == 1.0
    assert ref_range.high is None
    assert ref_range.text == 'low: 1.0 high: Positive'


def test_convert_record_lab_interpretation(
    observation_lab_record_interpretation,
    expected_observation_laboratory_interpretation
):

    result_data: List = convert_record("", observation_lab_record_interpretation)

    assert len(result_data) == 1
    fhir_record: Observation = Observation.parse_obj(result_data[0].dict())

    assert fhir_record.resource_type == "Observation"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 2  # PI, extID
    expected_resource = Observation(**expected_observation_laboratory_interpretation)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex,
    ).pretty()
    assert diff == "", diff


@ pytest.fixture
def observation_vitals_record_without_patientId():
    return {
        "accountNumber": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "encounterNumber": "ENC1111",
        "encounterInternalId": "hospa_ENC1111",
        "observationCodeText": "TEMPF",
        "observationDateTime": "2020-10-10T18:31:00.000Z",
        "observationValue": "98.2",
        "observationStatus": "final",
        "observationValueDataType": "valueQuantity",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


@ pytest.fixture
def expected_observation_vitals_record():
    return {
        "resourceType": "Observation",
        "id": "396c7168-93f4-11ec-a7e7-8c8590ba7dbd",
        "encounter": {"reference": "Encounter/hospa-ENC1111"},
        "identifier": [
            {
                "id": "AN.hospa-ENC1111",
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
                "value": "hospa_ENC1111"
            },
            {
                "id": "VN.ENC1111",
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
                "value": "ENC1111",
            },
            {
                "id": "extID",
                "system": "urn:id:extID",
                "value": "20201010183100-TEMPF"
            }
        ],
        "status": "final",
        "code": {"text": "TEMPF"},
        "subject": {"reference": "Patient/Hello-world-"},
        "valueQuantity": {"value": 98.2},
        "effectiveDateTime": "2020-10-10T18:31:00+00:00"
    }


def test_convert_record_vitals_signs(
    observation_vitals_record_without_patientId, expected_observation_vitals_record
):
    result_data: List = convert_record(
        "Hello_world!", observation_vitals_record_without_patientId
    )
    assert len(result_data) == 1

    fhir_record: Observation = Observation.parse_obj(result_data[0].dict())

    assert fhir_record.resource_type == "Observation"
    assert fhir_record.identifier
    assert len(fhir_record.identifier) == 3  # Account Number, VN, extID
    expected_resource = Observation(**expected_observation_vitals_record)
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_record.dict(),
        verbose_level=2,
        ignore_order=True,
        exclude_regex_paths=exclude_regex,
    ).pretty()
    assert diff == "", diff


@ pytest.fixture
def observation_lab_record_value_type_check():
    return {
        "observationCategory": "laboratory",
        "accountNumber": "hospa_ENC1111",
        "encounterNumber": "ENC1111",
        "encounterInternalId": "hospa_ENC1111",
        "assigningAuthority": "hospa",
        "patientInternalId": "1-1.12345",
        "observationCode": "718-7",
        "observationCodeSystem": "http://loinc.org",
        "observationCodeText": "Hemoglobin",
        "observationValue": "15.2",
        "observationValueUnits": "g/dL",
        "observationRefRangeText": "12.0-16.0",
        "observationDateTime": "2021-10-11T20:53:00.000Z",
        "observationInterpretationCode": "N",
        "filePath": "/home/csv/input.csv",
        "rowNum": 1
    }


def test_convert_record_lab_value_type_missing_qty_check(
    observation_lab_record_value_type_check,
    expected_observation_laboratory,
):
    result_data: List = convert_record("", observation_lab_record_value_type_check)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_obs: Observation = Observation.parse_obj(result_data[0])

    expected_resource = Observation(**expected_observation_laboratory)
    expected_resource.performer = None
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_obs.dict(),
        ignore_order=True,
        exclude_regex_paths=exclude_regex, ignore_numeric_type_changes=True
    ).pretty()
    assert diff == ""


def test_convert_record_lab_value_type_missing_int_check(
    observation_lab_record_value_type_check,
    expected_observation_laboratory,
):
    # "observationValue": "15.2",
    # "observationValueUnits": "g/dL",
    # "observationRefRangeText": "12.0-16.0",
    observation_lab_record_value_type_check["observationValue"] = "15"
    observation_lab_record_value_type_check["observationValueUnits"] = None

    result_data: List = convert_record("", observation_lab_record_value_type_check)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_obs: Observation = Observation.parse_obj(result_data[0])

    expected_resource = Observation(**expected_observation_laboratory)
    expected_resource.performer = None
    expected_resource.valueQuantity = None
    expected_resource.valueInteger = 15
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_obs.dict(),
        ignore_order=True,
        exclude_regex_paths=exclude_regex, ignore_numeric_type_changes=True
    ).pretty()
    assert diff == ""


def test_convert_record_lab_value_type_missing_STR_check(
    observation_lab_record_value_type_check,
    expected_observation_laboratory,
):
    # "observationValue": "15.2",
    # "observationValueUnits": "g/dL",
    # "observationRefRangeText": "12.0-16.0",
    observation_lab_record_value_type_check["observationValue"] = "High"
    observation_lab_record_value_type_check["observationValueUnits"] = None
    observation_lab_record_value_type_check["observationRefRangeText"] = "low-med"

    result_data: List = convert_record("", observation_lab_record_value_type_check)

    assert len(result_data) == 1
    # loading into fhir.resource test validity of the object
    fhir_obs: Observation = Observation.parse_obj(result_data[0])

    expected_resource = Observation(**expected_observation_laboratory)
    expected_resource.performer = None
    expected_resource.valueQuantity = None
    expected_resource.valueString = "High"
    expected_resource.referenceRange[0].low = None
    expected_resource.referenceRange[0].high = None
    expected_resource.referenceRange[0].text = "low-med"
    exclude_regex = [r"root\['id'\]"]
    diff = DeepDiff(
        expected_resource.dict(),
        fhir_obs.dict(),
        ignore_order=True,
        exclude_regex_paths=exclude_regex, ignore_numeric_type_changes=True
    ).pretty()
    assert diff == ""
