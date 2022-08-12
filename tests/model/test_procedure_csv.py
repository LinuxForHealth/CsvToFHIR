
# Test SSN removal of invalid values
import pytest

from linuxforhealth.csvtofhir.model.csv.procedure import ProcedureCsv


@pytest.mark.parametrize(
    "modifiers, expected_result",
    [
        (None, None),
        (["TG", "GY", "10"], ["TG", "GY", "10"]),
        ("TGGY10 ", ["TG", "GY", "10"]),
        ("TG GY 10", ["TG", "GY", "10"]),
        (" TG GY 10", ["TG", "GY", "10"]),
        ("TG, GY , 10", ["TG", "GY", "10"]),
        ("TG, GY , 10, ", ["TG", "GY", "10"])
    ]
)
def test_procedure_modifiers_split(modifiers, expected_result):
    pr: ProcedureCsv = ProcedureCsv.construct(procedureModifierList=modifiers)

    assert pr.get_modifier_list() == expected_result
