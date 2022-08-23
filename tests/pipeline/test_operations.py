from typing import Callable, List

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from linuxforhealth.csvtofhir.model.contract import DataContract, FileDefinition, Task
from linuxforhealth.csvtofhir.pipeline.operations import execute, parse


def test_parse(data_contract_model: DataContract):
    """
    Validates the pipeline parse function

    :param data_contract_model: The DataContract model fixture
    """
    file_definition: FileDefinition = data_contract_model.fileDefinitions[
        "Patient"
    ]
    result: List[Callable] = parse(file_definition.tasks)

    assert len(result) == 5

    expected_functions = [
        "add_constant",  # ssnSystem
        "format_date",
        "map_codes",
        "map_codes",
        "rename_columns"
    ]
    # partial functions provide access to the name attribute through func.__name__
    # our first function is not wrapped with partial, so it just uses __name__
    actual_functions = []
    for r in result:
        if hasattr(r, "func"):
            func_name = r.func.__name__
        else:
            func_name = r.__name__
        actual_functions.append(func_name)

    assert expected_functions == actual_functions


def test_execute(
    data_contract_model: DataContract,
    input_data_frame: DataFrame,
    expected_data_frame: DataFrame,
):
    """
    Tests pipeline execution using a sample DataContract resource. Pipeline tasks within the
    DataContract include:
    - add_row_num
    - set_nan_to_none
    - add_constant
    - format_date
    - map_codes
    - rename_columns

    :param data_contract_model: The input data contract fixture
    :param input_data_frame: The input data frame used to kick-off the pipeline
    :param expected_data_frame: The expected data frame output
    """
    input_data_frame["dateOfBirth"] = ["07-06-1951"]

    expected_data_frame.drop(
        axis=1,
        columns=[
            "patientId",
            "hospitalId",
            "givenName",
            "familyName",
            "sex",
            "dateOfBirth"
        ],
        inplace=True
    )

    expected_data_frame["patientInternalId"] = ["MRN1234"]
    expected_data_frame["assigningAuthority"] = ["hospa"]
    expected_data_frame["birthDate"] = ["1951-07-06"]
    expected_data_frame["gender"] = ["male"]
    expected_data_frame["nameFirstMiddle"] = ["Thomas"]
    expected_data_frame["nameLast"] = ["Jones"]
    expected_data_frame["notNumber"] = [None]
    expected_data_frame["rowNum"] = [1]

    file_definition: FileDefinition = data_contract_model.fileDefinitions[
        "Patient"
    ]

    tasks = [Task(name="add_row_num"), Task(name="set_nan_to_none")] + file_definition.tasks
    result: DataFrame = execute(tasks, input_data_frame)
    result.sort_index(axis=1, inplace=True)
    expected_data_frame.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, result)
