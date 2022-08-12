
# Test SSN removal of invalid values
import pytest

from linuxforhealth.csvtofhir.model.csv.patient import PatientCsv


@pytest.mark.parametrize(
    "patient_ssn, expected_result",
    [
        ("020-11-7890", "020117890"),
        ("020997890", "020997890"),
        ("0000-11-7890", None),
        ("", None),
        ("999-99-9999", None),
        ("000-00-0000", None)
    ]
)
def test_patient_ssn_validations(patient_ssn, expected_result):

    pat_dictionary = {
        "ssn": patient_ssn,
        "ssnSystem": "http://hl7.org/fhir/sid/us-ssn",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }
    patient: PatientCsv = PatientCsv.parse_obj(pat_dictionary)
    if expected_result:
        assert patient.ssn == expected_result
    else:
        assert patient.ssn is None


def test_patient_system_defaults():
    pat_dictionary = {
        "patientInternalId": "1212121212",
        "filePath": "/home/csv/input.csv",
        "rowNum": 0
    }
    patient: PatientCsv = PatientCsv.parse_obj(pat_dictionary)
    patient.raceSystem = "http://terminology.hl7.org/CodeSystem/v3-Race"
    patient.ethnicitySystem = "http://terminology.hl7.org/CodeSystem/v2-0189"
