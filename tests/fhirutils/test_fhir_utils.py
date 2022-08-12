import pytest

from linuxforhealth.csvtofhir.fhirutils import fhir_utils, fhir_constants

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta
from fhir.resources.observation import Observation


@pytest.mark.parametrize(
    "input_value, output_value",
    [
        ("hospa", "urn:id:hospa"),
        (None, None),
        ("urn:id:hospb", "urn:id:hospb"),
        ("http://something", "http://something"),
    ],
)
def test_validate_uri_format(input_value: str, output_value: str):
    assert fhir_utils.get_uri_format(input_value) == output_value


@pytest.mark.parametrize(
    "id, expected_result",
    [
        ("020-11-7890", "020-11-7890"),
        ("020.11.7890", "020.11.7890"),
        ("0000_11_7890", "0000-11-7890"),
        ("", None),
        ("SS #illegalC@H test", "SS--illegalC-H-test")
    ]
)
def test_internal_id_validations(id, expected_result):
    assert fhir_utils.format_id_datatype(id) == expected_result


@pytest.mark.parametrize(
    "boolean_string, expected_result",
    [
        ("True", True),
        ("False", True),
        ("SomethingElse", False),
        ("", False),
        (None, False)
    ]
)
def test_is_boolean_value(boolean_string, expected_result):
    assert fhir_utils.is_boolean_value(boolean_string) == expected_result


@pytest.mark.parametrize(
    "boolean_string, expected_result",
    [
        ("True", True),
        ("False", False),
        ("SomethingElse", None),
        (None, None),
    ]
)
def test_get_boolean_value(boolean_string, expected_result):
    assert fhir_utils.get_boolean_value(boolean_string) == expected_result


@pytest.mark.parametrize(
    "input, expected_result, tz",
    [
        ("2020-01-28 13:40", "2020-01-28T13:40:00", None),
        ("2022-10-02 9:30", "2022-10-02T09:30:00-04:00", "US/Eastern"),
        ("2022-3-02 9:30", "2022-03-02T09:30:00-05:00", "US/Eastern")  # Summer different due to DST
    ]
)
def test_date_format(input, expected_result, tz):
    result = fhir_utils.get_datetime(input, tz).isoformat()
    assert str(result) == expected_result


@pytest.mark.parametrize(
    "start, end, expected_start, expected_end, tz",
    [
        ("2020-01-28 13:40", "2020-01-28 13:41", "2020-01-28T13:40:00", "2020-01-28T13:41:00", None),
        ("2022-10-02 9:30", "2022-10-02 9:31", "2022-10-02T09:30:00-04:00", "2022-10-02T09:31:00-04:00", "US/Eastern")
    ]
)
def test_time_period_format(start, end, expected_start, expected_end, tz):
    result = fhir_utils.get_fhir_type_period(start, end, tz)
    assert str(result.start.isoformat()) == expected_start
    assert str(result.end.isoformat()) == expected_end


@pytest.mark.parametrize(
    "code, display, system, text, fhir_type, extId_value",
    [
        # System in preferred list
        ("111", None, fhir_constants.SystemConstants.SNOMED_SYSTEM, None, "Condition", "111-SNOMED"),
        # System not in preferred list
        ("222", None, fhir_constants.SystemConstants.RXNORM_SYSTEM, None, "Condition", "222-RXNORM"),
        # System not recognized, starting with "urn:id"
        ("333", None, "urn:id:mysys", None, "Condition", "333-mysys"),
        # No system
        ("444", None, None, None, "Condition", "444"),
        # No code, but have display
        (None, "Test display", None, None, "Condition", "Test display"),
        # Text only
        (None, None, None, "My text", "Condition", "My text")
    ]
)
def test_extID_identifier(code, display, system, text, fhir_type, extId_value):
    if code or display or system:
        coding = Coding.construct(code=code, display=display, system=system)
        cc = CodeableConcept.construct(coding=[coding], text=text)
    else:
        cc = CodeableConcept.construct(text=text)
    result = fhir_utils.get_external_identifier(cc, fhir_type)
    assert result.system == "urn:id:extID"
    assert result.id == "extID"
    assert result.value == extId_value


def test_extID_identifier_observation():
    # Test using effectiveDateTime for the timestamp
    coding = Coding.construct(code="111", system=fhir_constants.SystemConstants.LOINC_SYSTEM)
    cc = CodeableConcept.construct(coding=[coding])
    extension = Extension.construct(
        url="http://ibm.com/fhir/cdm/StructureDefinition/process-timestamp",
        valueDateTime=fhir_utils.get_datetime("2022-03-30T13:32:32.133078+00:00")
    )
    meta = Meta.construct(extension=[extension])
    observation = Observation.construct(
        code=cc,
        effectiveDateTime=fhir_utils.get_datetime("2021-10-11T00:00:00Z"),
        meta=meta
    )
    result = fhir_utils.get_external_identifier(cc, "Observation", observation)
    assert result.system == "urn:id:extID"
    assert result.id == "extID"
    assert result.value == "20211011000000-111-LOINC"

    # Test using meta process-timestamp for the timestamp, code has only text
    cc = CodeableConcept.construct(text="bmi")
    observation = Observation.construct(
        code=cc,
        meta=meta
    )
    result = fhir_utils.get_external_identifier(cc, "Observation", observation)
    assert result.system == "urn:id:extID"
    assert result.id == "extID"
    assert result.value == "20220330133232-bmi"
