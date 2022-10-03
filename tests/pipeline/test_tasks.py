from datetime import date
import math
import os
from typing import List

import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from linuxforhealth.csvtofhir.config import ConverterConfig
from linuxforhealth.csvtofhir.pipeline import tasks
from linuxforhealth.csvtofhir.pipeline.tasks import (add_constant, add_row_num, append_list,
                                                     change_case, compare_to_date,
                                                     conditional_column, conditional_column_update,
                                                     conditional_column_with_prerequisite,
                                                     convert_to_list, copy_columns,
                                                     filter_to_columns, find_not_null_value,
                                                     format_date, map_codes,
                                                     remove_whitespace_from_columns,
                                                     rename_columns, replace_text,
                                                     set_nan_to_none, split_column, split_row,
                                                     validate_value, join_data)
from tests.support import resources_directory


@pytest.fixture
def converter_config(data_contract_directory):
    """
    ConverterConfig fixture with a directory configured to tests/resources
    :param data_contract_directory: The data contract directory fixture
    :return: The ConverterConfig fixture
    """
    return ConverterConfig(mapping_config_directory=data_contract_directory)


def test_add_constant(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates that add_constant adds additional columns to a data frame.

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame: The expected data frame, used for comparisons
    """
    expected_data_frame["ethnicitySystem"] = [
        "http://terminology.hl7.org/CodeSystem/v3-Ethnicity"
    ]
    expected_data_frame["raceSystem"] = [
        "http://terminology.hl7.org/CodeSystem/v3-Race"
    ]

    result: DataFrame = add_constant(
        input_data_frame,
        "ethnicitySystem",
        "http://terminology.hl7.org/CodeSystem/v3-Ethnicity"
    )
    result: DataFrame = add_constant(
        result, "raceSystem", "http://terminology.hl7.org/CodeSystem/v3-Race"
    )

    assert_frame_equal(expected_data_frame, result)


def test_filter_to_columns():

    # c1 is the source column to be filtered, c2 is present to prove other columns untouched
    input_data = [{'c1': 'W', 'c2': 'WW'}, {'c1': 'X', 'c2': 'XX'}, {'c1': 'Y', 'c2': 'YY'}, {'c1': 'Z', 'c2': 'ZZ'}]
    input_data_frame = pd.DataFrame(input_data)

    # The test filters values of c1 to a column of XY, of Z, and anything else Other
    expected_output = [{'c1': 'W', 'c2': 'WW', 'XYs': None, 'Zs': None, 'Other': 'W'},
                       {'c1': 'X', 'c2': 'XX', 'XYs': 'X', 'Zs': None, 'Other': None},
                       {'c1': 'Y', 'c2': 'YY', 'XYs': 'Y', 'Zs': None, 'Other': None},
                       {'c1': 'Z', 'c2': 'ZZ', 'XYs': None, 'Zs': 'Z', 'Other': None}]

    expected_data_frame = pd.DataFrame(expected_output)

    actual_data_frame: DataFrame = filter_to_columns(
        input_data_frame, "c1", ["XYs", "Zs", "Other"], [['X', 'Y'], ['Z']]
    )

    assert_frame_equal(expected_data_frame, actual_data_frame)


def test_filter_to_columns_empty():

    # c1 is the source column to be filtered, c2 is present to prove other columns untouched
    input_data = [{'c1': 'W', 'c2': None}, {'c1': 'X', 'c2': 'XX'}]
    input_data_frame = pd.DataFrame(input_data)

    # The test filters values of c1 to a column of XY, of Z, and anything else Other
    expected_output = [{'c1': 'W', 'c2': None, 'c2copy': None},
                       {'c1': 'X', 'c2': 'XX', 'c2copy': 'XX'},
                       ]

    expected_data_frame = pd.DataFrame(expected_output)

    actual_data_frame: DataFrame = filter_to_columns(
        input_data_frame, "c2", ["c2copy"], []
    )

    assert_frame_equal(expected_data_frame, actual_data_frame)


def test_format_date(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates that the format_date task updates data columns correctly

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame: The expected data frame, used for comparisons
    """

    result: DataFrame = format_date(input_data_frame, ["dateOfBirth"])
    assert_frame_equal(expected_data_frame, result)

    expected_data_frame["dateOfBirth"] = ["07/06/1951"]
    result: DataFrame = format_date(input_data_frame, ["dateOfBirth"], "%m/%d/%Y")
    assert_frame_equal(expected_data_frame, result)


def test_task_rename_columns(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Tests rename_columns

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    expected_data_frame.drop(
        columns=[
            "patientId",
            "hospitalId",
            "givenName",
            "familyName",
            "dateOfBirth",
            "sex"
        ],
        inplace=True
    )

    expected_data_frame["patientInternalId"] = ["MRN1234"]
    expected_data_frame["assigningAuthority"] = ["hospa"]
    expected_data_frame["gender"] = ["M"]
    expected_data_frame["birthDate"] = ["1951-07-06"]
    expected_data_frame["nameFirstMiddle"] = ["Thomas"]
    expected_data_frame["nameLast"] = ["Jones"]

    column_map = {
        "patientId": "patientInternalId",
        "hospitalId": "assigningAuthority",
        "givenName": "nameFirstMiddle",
        "familyName": "nameLast",
        "dateOfBirth": "birthDate",
        "sex": "gender"
    }

    result: DataFrame = rename_columns(input_data_frame, column_map)
    expected_data_frame.sort_index(axis=1, inplace=True)
    result.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, result)


def test_set_nan_to_none(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates that set_nan_to_none sets Numpy nan values to None

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    expected_data_frame["notNumber"] = [None]
    result: DataFrame = set_nan_to_none(input_data_frame)
    assert_frame_equal(expected_data_frame, result)


def test_remove_whitespace_from_columns(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates test_remove_whitespace_from_columns strips whitespace
    from both the front and end of column names.

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame.rename(columns={"encounterId": " encounterId"}, inplace=True)
    input_data_frame.rename(columns={"patientId": "patientId "}, inplace=True)
    result: DataFrame = remove_whitespace_from_columns(input_data_frame)
    assert_frame_equal(expected_data_frame, result)


def test_map_codes(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates map_codes with default assignment handling

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    code_map = {"sex": {"default": "unknown", "M": "male", "F": "female", "O": "other"}}
    expected_data_frame["sex"] = ["male"]
    result: DataFrame = map_codes(input_data_frame, code_map)
    assert_frame_equal(expected_data_frame, result)

    # validate default values mapping.  A value unrecognized results in the default value.
    input_data_frame["sex"] = ["declined to answer"]
    expected_data_frame["sex"] = ["unknown"]
    result = map_codes(input_data_frame, code_map)
    assert_frame_equal(expected_data_frame, result)

    # validate missing values mapping. A missing value results in the default value.
    input_data_frame["sex"] = [np.nan]
    expected_data_frame["sex"] = ["unknown"]
    result = map_codes(input_data_frame, code_map)
    assert_frame_equal(expected_data_frame, result)


def test_map_codes_with_file(
    monkeypatch,
    converter_config,
    input_data_frame: DataFrame,
    expected_data_frame: DataFrame,
):
    """
    Validates map_codes with default assignment handling

    :param monkeypatch: The pytest monkeypatch fixture
    :param converter_config: ConverterConfig fixture configured to use tests/resources
    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    :param monkeypatch: The pytest monkeypatch fixture
    """
    monkeypatch.setattr(tasks, "get_converter_config", lambda: converter_config)

    code_map = {"sex": "sex.csv"}
    expected_data_frame["sex"] = ["male"]
    result: DataFrame = map_codes(input_data_frame, code_map)
    assert_frame_equal(expected_data_frame, result)

    # validate default values mapping
    input_data_frame["sex"] = ["declined to answer"]
    expected_data_frame["sex"] = ["unknown"]
    result = map_codes(input_data_frame, code_map)
    assert_frame_equal(expected_data_frame, result)


def test_copy_columns(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Tests copy_columns

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    expected_data_frame["fullName"] = ["Thomas Jones"]
    result: DataFrame = copy_columns(
        input_data_frame, ["givenName", "familyName"], "fullName"
    )
    assert_frame_equal(expected_data_frame, result)

    expected_data_frame["fullName"] = ["Thomas-Jones"]
    result: DataFrame = copy_columns(
        input_data_frame, ["givenName", "familyName"], "fullName", "-"
    )
    assert_frame_equal(expected_data_frame, result)

    expected_data_frame["fullName"] = ["Thomas Jones"]
    result: DataFrame = copy_columns(
        input_data_frame, ["givenName", "familyName"], "fullName", None
    )
    assert_frame_equal(expected_data_frame, result)

    # Tests when there are empty (None) columns for concatenation
    input_data_frame["empty1"] = None
    input_data_frame["empty2"] = None
    expected_data_frame["empty1"] = None
    expected_data_frame["empty2"] = None
    expected_data_frame["double_empty"] = "^"
    result: DataFrame = copy_columns(
        input_data_frame, ["empty1", "empty2"], "double_empty", "^"
    )
    assert_frame_equal(expected_data_frame, result)


def test_find_not_null_value():
    """
    Tests find_not_null_value
    """

    input_data_frame = DataFrame()

    # Valid value in each column, should pick first
    input_data_frame["value1"] = ["1.0"]
    input_data_frame["value2"] = ["Positive"]
    expected_data_frame = input_data_frame.copy(deep=True)
    expected_data_frame["value"] = ["1.0"]

    result: DataFrame = find_not_null_value(input_data_frame, ["value1", "value2"], "value")
    assert_frame_equal(expected_data_frame, result)

    # Valid value in first column, null in second column, should pick first
    input_data_frame = DataFrame()
    input_data_frame["value1"] = ["2.0"]
    input_data_frame["value2"] = [None]
    expected_data_frame = input_data_frame.copy(deep=True)
    expected_data_frame["value"] = ["2.0"]

    result: DataFrame = find_not_null_value(input_data_frame, ["value1", "value2"], "value")
    assert_frame_equal(expected_data_frame, result)

    # NaN in first column, valid value in second column, should pick secound
    input_data_frame = DataFrame()
    input_data_frame["value1"] = [np.NaN]
    input_data_frame["value2"] = ["Positive"]
    expected_data_frame = input_data_frame.copy(deep=True)
    expected_data_frame["value1"] = None  # task will update NaN to None
    expected_data_frame["value"] = ["Positive"]

    result: DataFrame = find_not_null_value(input_data_frame, ["value1", "value2"], "value")
    assert_frame_equal(expected_data_frame, result)

    # None in first column, NaN in second column, valid value in third column, should pick third
    input_data_frame = DataFrame()
    input_data_frame["value1"] = [None]
    input_data_frame["value2"] = [np.NaN]
    input_data_frame["value3"] = ["4.0"]
    expected_data_frame = input_data_frame.copy(deep=True)
    expected_data_frame["value2"] = None  # task will update NaN to None
    expected_data_frame["value"] = ["4.0"]

    result: DataFrame = find_not_null_value(input_data_frame, ["value1", "value2", "value3"], "value")
    assert_frame_equal(expected_data_frame, result)

    # Three rows of data, to make sure each is handled correctly
    input_data_frame = DataFrame()
    input_data_frame["value1"] = pd.Series([np.NaN, 1.0, np.NaN])
    input_data_frame["value2"] = pd.Series(["Negative", "3", None])
    expected_data_frame = input_data_frame.copy(deep=True)
    expected_data_frame["value"] = pd.Series(["Negative", 1.0, None])
    # Loading None into a series for a data frame automatically changes None to NaN
    # Expected result is actually a None, so updating expected data frame from NaN to None
    expected_data_frame = expected_data_frame.replace(np.nan, None)

    result: DataFrame = find_not_null_value(input_data_frame, ["value1", "value2"], "value")
    assert_frame_equal(expected_data_frame, result)


def test_split_columns_task(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Validates that split_columns creates additional rows within a DataFrame as expected.

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["A"] = ["1"]
    input_data_frame["B"] = ["2"]

    expected_data_frame = pd.DataFrame(
        np.repeat(expected_data_frame.values, 2, axis=0),
        columns=expected_data_frame.columns,
    )
    expected_data_frame["columnLabel"] = ["A", "B"]
    expected_data_frame["columnValue"] = ["1", "2"]

    result = split_row(input_data_frame, ["A", "B"], "columnLabel", "columnValue")
    assert_frame_equal(expected_data_frame, result, check_dtype=False)

    result = split_row(input_data_frame, [], "columnLabel", "columnValue")
    assert_frame_equal(input_data_frame, result)


def test_conditional_column_task():
    """
    Validates that conditional_column creates a mapped column result in a DataFrame as expected.
    """
    condition_map = {
        "64328": "IL",
        "90210": "CA",
        "29302": "SC",
        "default": "NY"
    }
    input_data_frame = DataFrame()
    input_data_frame["zip"] = ["64328"]
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["IL"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = ["90210"]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = ["CA"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = ["29302"]
    expected_data_frame["zip"] = ["29302"]
    expected_data_frame["state"] = ["SC"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = [None]
    expected_data_frame["zip"] = [None]
    expected_data_frame["state"] = ["NY"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)


def test_conditional_column_task_with_filename(monkeypatch, converter_config):
    """
    Validates that conditional_column creates a mapped column result based on file input, in a DataFrame as expected.

    :param monkeypatch: The pytest monkeypatch fixture
    :param converter_config: ConverterConfig fixture configured to use tests/resources
    """
    monkeypatch.setattr(tasks, "get_converter_config", lambda: converter_config)

    condition_map = "zip_states.csv"

    input_data_frame = DataFrame()
    expected_data_frame = DataFrame()

    input_data_frame["zip"] = ["64328"]
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["IL"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = ["90210"]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = ["CA"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = ["29302"]
    expected_data_frame["zip"] = ["29302"]
    expected_data_frame["state"] = ["SC"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)

    input_data_frame["zip"] = [None]
    expected_data_frame["zip"] = [None]
    expected_data_frame["state"] = ["NY"]
    result: DataFrame = conditional_column(
        input_data_frame, "zip", condition_map, "state"
    )
    assert_frame_equal(expected_data_frame, result)


def test_conditional_column_update():
    """
    Validates that conditional_column_update updates a column with a newly mapped value
    """
    condition_map = {
        "64328": "IL",
        "90210": "CA"
    }

    # Case 1:  a specific zip, map and update state column
    input_data_frame = DataFrame()
    input_data_frame["zip"] = ["90210"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_update(
        input_data_frame, "zip", condition_map, "state")
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = ["CA"]
    assert_frame_equal(expected_data_frame, result)

    # Case 2:  multiple rows to map and update state column
    input_data_frame = DataFrame()
    input_data_frame["zip"] = pd.Series(["90210", "64328"])
    input_data_frame["state"] = pd.Series(["UT", "UT"])
    result: DataFrame = conditional_column_update(
        input_data_frame, "zip", condition_map, "state")
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = pd.Series(["90210", "64328"])
    expected_data_frame["state"] = pd.Series(["CA", "IL"])
    assert_frame_equal(expected_data_frame, result)

    # Case 3: one zip is not in mapping dictionary, so it should stay as-is as there is no default
    input_data_frame = DataFrame()
    input_data_frame["zip"] = pd.Series(["90210", "55901"])
    input_data_frame["state"] = pd.Series(["UT", "MN"])
    result: DataFrame = conditional_column_update(
        input_data_frame, "zip", condition_map, "state")
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = pd.Series(["90210", "55901"])
    expected_data_frame["state"] = pd.Series(["CA", "MN"])
    assert_frame_equal(expected_data_frame, result)

    condition_map = {
        "64328": "IL",
        "90210": "CA",
        "default": "NY"
    }

    # Case 4:  condition map includes a default and specific zip not in condition_map, should use default
    input_data_frame = DataFrame()
    input_data_frame["zip"] = ["10001"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_update(
        input_data_frame, "zip", condition_map, "state")
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = ["10001"]
    expected_data_frame["state"] = ["NY"]
    assert_frame_equal(expected_data_frame, result)


def test_conditional_column_with_prerequisite():
    """
    Validates that conditional_column_with_prerequisite creates a mapped column result in a DataFrame only when
    the correct prerequisite is met.
    """
    # We create a contrived situation to test the logic.
    # Case 1:  a specific zip, a null city, we want to
    # empty or null out the state as its wrong
    # Case 2:  a specific zip, a null city, we want to set the state to
    # a new correct state code
    condition_map = {
        "64328": "IL",
        "90210": None,
        "29302": "SC",
        "default": "NY"
    }

    # Case 1a:  a specific zip, a null city, match looking for empty, then map (null out) the state.
    input_data_frame = DataFrame()
    input_data_frame["city"] = [None]
    input_data_frame["zip"] = ["90210"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = [None]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = [None]
    assert_frame_equal(expected_data_frame, result)

    # Case 1b:  a specific zip, a null city, match looking for content (should fail), then leave the state as it was.
    input_data_frame = DataFrame()
    input_data_frame["city"] = [None]
    input_data_frame["zip"] = ["90210"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", ".*")
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = [None]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = ["UT"]
    assert_frame_equal(expected_data_frame, result)

    # Case 1c:  a specific zip, a non-null city, match looking for any content, then map (null out) the state.
    input_data_frame = DataFrame()
    input_data_frame["city"] = ["Beverly Hills"]
    input_data_frame["zip"] = ["90210"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", ".*")
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = ["Beverly Hills"]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = [None]
    assert_frame_equal(expected_data_frame, result)

    # Case 1d:  a specific zip, a non-null city, match looking for empty, then (fail) leave the state as it was.
    input_data_frame = DataFrame()
    input_data_frame["city"] = ["Beverly Hills"]
    input_data_frame["zip"] = ["90210"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = ["Beverly Hills"]
    expected_data_frame["zip"] = ["90210"]
    expected_data_frame["state"] = ["UT"]
    assert_frame_equal(expected_data_frame, result)

    # Case 2a:  a specific zip, a null city, match looking for empty, then map (actual value) the state.
    input_data_frame = DataFrame()
    input_data_frame["city"] = [None]
    input_data_frame["zip"] = ["64328"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = [None]
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["IL"]
    assert_frame_equal(expected_data_frame, result)

    # Case 2b:  a specific zip, a null city, match looking for content (should fail), then leave the state as it was.
    input_data_frame = DataFrame()
    input_data_frame["city"] = [None]
    input_data_frame["zip"] = ["64328"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", ".*")
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = [None]
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["UT"]
    assert_frame_equal(expected_data_frame, result)

    # Case 2c:  a specific zip, a non-null city, match looking for any content, then map the new state.
    input_data_frame = DataFrame()
    input_data_frame["city"] = ["Chicago"]
    input_data_frame["zip"] = ["64328"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", ".*")
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = ["Chicago"]
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["IL"]
    assert_frame_equal(expected_data_frame, result)

    # Case 2d:  a specific zip, a non-null city, match looking for empty, then (fail) leave the state as it was.
    input_data_frame = DataFrame()
    input_data_frame["city"] = ["Chicago"]
    input_data_frame["zip"] = ["64328"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = ["Chicago"]
    expected_data_frame["zip"] = ["64328"]
    expected_data_frame["state"] = ["UT"]
    assert_frame_equal(expected_data_frame, result)

    # Case 3d:  a specific zip not in condition=map, should use default
    input_data_frame = DataFrame()
    input_data_frame["city"] = [None]
    input_data_frame["zip"] = ["10001"]
    input_data_frame["state"] = ["UT"]
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["city"] = [None]
    expected_data_frame["zip"] = ["10001"]
    expected_data_frame["state"] = ["NY"]
    assert_frame_equal(expected_data_frame, result)

    # No default in map
    condition_map = {
        "64328": "IL",
        "90210": None,
        "29302": "SC"
    }

    # Case 3a: multiple rows to map and update state column
    input_data_frame = DataFrame()
    input_data_frame["zip"] = pd.Series(["90210", "64328"])
    input_data_frame["state"] = pd.Series(["UT", "UT"])
    input_data_frame["city"] = pd.Series([None, None])
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = pd.Series(["90210", "64328"])
    expected_data_frame["state"] = pd.Series([None, "IL"])
    expected_data_frame["city"] = pd.Series([None, None])
    assert_frame_equal(expected_data_frame, result)

    # Case 3b: one zip is not in mapping dictionary, so it should stay as-is
    input_data_frame = DataFrame()
    input_data_frame["zip"] = pd.Series(["90210", "55901"])
    input_data_frame["state"] = pd.Series(["UT", "MN"])
    input_data_frame["city"] = pd.Series([None, None])
    result: DataFrame = conditional_column_with_prerequisite(
        input_data_frame, "zip", condition_map, "state", "city", None)
    expected_data_frame = DataFrame()
    expected_data_frame["zip"] = pd.Series(["90210", "55901"])
    expected_data_frame["state"] = pd.Series([None, "MN"])
    expected_data_frame["city"] = pd.Series([None, None])
    assert_frame_equal(expected_data_frame, result)


def test_split_column_delimiter(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates split_column when a delimiter is used

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["CSV,2,FHIR"]

    expected_data_frame["awesomeColumn"] = ["CSV,2,FHIR"]
    expected_data_frame["A"] = ["CSV"]
    expected_data_frame["B"] = ["2"]
    expected_data_frame["C"] = ["FHIR"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    actual: DataFrame = split_column(
        input_data_frame, "awesomeColumn", ["A", "B", "C"], delimiter=","
    )
    actual.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, actual)


def test_split_column_delimiter_mixed(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates split_column when a delimiter is used

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["14 mL"]

    expected_data_frame["awesomeColumn"] = ["14 mL"]
    expected_data_frame["Dosage"] = ["14"]
    expected_data_frame["Units"] = ["mL"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    actual: DataFrame = split_column(
        input_data_frame, "awesomeColumn", ["Dosage", "Units"], delimiter=" "
    )
    actual.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, actual)


def test_split_column_delimiter_not_found(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates split_column behavior when a delimiter is used, but not matched in the subject cell.
    Should put all the input text into the first column result and an empty following column

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["14"]

    expected_data_frame["awesomeColumn"] = ["14"]
    expected_data_frame["Dosage"] = ["14"]
    expected_data_frame["Units"] = [None]
    expected_data_frame.sort_index(axis=1, inplace=True)

    actual: DataFrame = split_column(
        input_data_frame, "awesomeColumn", ["Dosage", "Units"], delimiter=" "
    )
    actual.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, actual)


def test_split_column_indices(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Validates split_column where indices are used

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["CSVToFHIR"]

    expected_data_frame["awesomeColumn"] = ["CSVToFHIR"]
    expected_data_frame["A"] = ["CSV"]
    expected_data_frame["B"] = ["To"]
    expected_data_frame["C"] = ["FHIR"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    actual: DataFrame = split_column(
        input_data_frame,
        "awesomeColumn",
        ["A", "B", "C"],
        indices=((0, 3), (3, 5), (5, 9))
    )
    actual.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, actual)


def test_split_column_indices_invalid_new_column_length(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Validates that split_column raises a ValueError when the number of new columns does not match the index length.

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["csvtofhir"]

    expected_data_frame["awesomeColumn"] = ["csvtofhir"]
    expected_data_frame["A"] = ["CSV"]
    expected_data_frame["B"] = ["2"]
    expected_data_frame["C"] = ["FHIR"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    with pytest.raises(ValueError) as exec_info:
        split_column(
            input_data_frame,
            "awesomeColumn",
            ["A", "B"],
            indices=((0, 3), (3, 4), (4, 8))
        )

    assert "The number of index pairs" in str(exec_info.value)


def test_split_column_indices_invalid_indices(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Validates that split_column raises a ValueError when the number of indices is not 2 for a single Tuple entry.

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["csvtofhir"]

    expected_data_frame["awesomeColumn"] = ["csvtofhir"]
    expected_data_frame["A"] = ["CSV"]
    expected_data_frame["B"] = ["2"]
    expected_data_frame["C"] = ["FHIR"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    with pytest.raises(ValueError) as exec_info:
        split_column(
            input_data_frame,
            "awesomeColumn",
            ["A", "B", "C"],
            indices=[[0, 3, 1], [3, 4], [4, 8]]
        )

    assert "Index boundaries may contain 1 or 2 elements" in str(exec_info.value)

    with pytest.raises(ValueError) as exec_info:
        split_column(
            input_data_frame,
            "awesomeColumn",
            ["A", "B", "C"],
            indices=[[], [3, 4], [4, 8]]
        )

    assert "Index boundaries may contain 1 or 2 elements" in str(exec_info.value)


def test_split_column_indices_open_index(
    input_data_frame: DataFrame, expected_data_frame: DataFrame
):
    """
    Validates that split_column parses when an index boundary contains an open ending index .

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame:  The expected data frame, used for comparisons
    """
    input_data_frame["awesomeColumn"] = ["csvtofhir"]

    expected_data_frame["awesomeColumn"] = ["csvtofhir"]
    expected_data_frame["A"] = ["csv"]
    expected_data_frame["B"] = ["fhir"]
    expected_data_frame.sort_index(axis=1, inplace=True)

    actual = split_column(
        input_data_frame,
        "awesomeColumn",
        ["A", "B"],
        indices=[[0, 3], [5]]
    )

    actual.sort_index(axis=1, inplace=True)
    assert_frame_equal(expected_data_frame, actual)


@ pytest.mark.parametrize(
    "original_string, match, replacement, options, expected_result",
    [
        # - - - - - - General Functional Tests - - - - - -
        # both t's in Matthew should be replaced
        ("Matthew", "t", "@", "", "Ma@@hew"),
        # Only lowercase s's should be replaced (default is case sensitive)
        ("Sue1ss", "s", "@", "", "Sue1@@"),
        # All S's should be replaced, case insensitive option used
        ("Sue2ss", "s", "@", "CASE_INSENSITIVE", "@ue2@@"),
        # Just the first S should be replaced because it is at the beginning (case insensitive option used)
        ("Sue3ss", "s", "@", "BEGIN CASE_INSENSITIVE", "@ue3ss"),
        # The first S should not be matched, because no small s at beginning
        ("Sue4ss", "s", "@", "BEGIN", "Sue4ss"),
        # Just the last S should be replaced because it is at the end (case insensitive option used)
        ("Sue5ss", "S", "@", "END CASE_INSENSITIVE", "Sue5s@"),
        # The last s should not be matched, because no small s at end
        ("Sue6ss", "S", "@", "END", "Sue6ss"),
        # BEGIN and END together should work with case insensitive
        ("Sue7ss", "S", "@", "BEGIN END CASE_INSENSITIVE", "@ue7s@"),
        # BEGIN and END together should work with exact case.  Only s at begin and end should replace.
        ("suSse8ss", "s", "@", "BEGIN END", "@uSse8s@"),
        # Special regex characters should be seen as regular because regex option not used
        ("Sue9ss", "s", "[]", "CASE_INSENSITIVE", "[]ue9[][]"),
        ("Name [Nickname]", "[", "|", "CASE_INSENSITIVE", "Name |Nickname]"),
        # Searching for regexy characters should work like regular characters if REGEX option not set
        # This case should match
        ("[AB]1", "[AB]", "X", "", "X1"),
        # This case should not match
        ("AB2", "[AB]", "X", "", "AB2"),
        # However, if REXEG is specified, it should match
        ("[AB]3", "[AB]", "X", "REGEX", "[XX]3"),
        # REGEX option takes priority over all others.  Here CASE_INSENSITIVE is ignored
        ("[Ab]4", "[AB]", "X", "REGEX, CASE_INSENSITIVE", "[Xb]4"),
        # REGEX option takes priority over all others.  Here CASE_INSENSITIVE is ignored
        ("[AB]5", "[Ab]", "X", "REGEX, CASE_INSENSITIVE", "[XB]5"),
        # When using REGEX, if case insensitivity is desired it must be built into the regex
        ("[Ab]6", "[AaBb]", "X", "REGEX", "[XX]6"),
        # Another example of case insensitivity using Regex.
        ("[Ab]7", "(?i)ab", "X", "REGEX", "[X]7"),
        # Test of REGEX capture groups.  Format a telephone number.  Escape
        # character \ must be doubled because passed in string.
        (
            "1234567890",
            "([0-9]{3})([0-9]{3})([0-9]{4})",
            "(\\1)\\2-\\3",
            "REGEX",
            "(123)456-7890"
        ),
        # - - - - - - Domain Specific Tests - - - - - -
        # Removes 'MDX - ' and 'MS - ' prefixes from allergies column
        # Remove the first MDX -
        (
            "MDX - Sulfamethoxazole1 MDX -",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "Sulfamethoxazole1 MDX -"
        ),
        # Remove the first MDX -
        (
            "MDX-Sulfamethoxazole2 MDX-",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "Sulfamethoxazole2 MDX-"
        ),
        # Won't match the first MDX, because there is no separator after MDX
        (
            "MDX Sulfamethoxazole3 MDX",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "MDX Sulfamethoxazole3 MDX"
        ),
        # This will match a first MDX with or without a -
        (
            "MDX Sulfamethoxazole3 MDX",
            "^(MDX|MS) {0,3}-{0,1} {0,3}",
            "",
            "REGEX",
            "Sulfamethoxazole3 MDX"
        ),
        # Remove the first MS
        (
            "MS - Sulfamethoxazole4 MS",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "Sulfamethoxazole4 MS"
        ),
        # Remove the first MS
        (
            "MS-Sulfamethoxazole5 MS",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "Sulfamethoxazole5 MS"
        ),
        # Won't match the first MS, because there is no separator after MS
        (
            "MS Sulfamethoxazole6 MS",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "MS Sulfamethoxazole6 MS"
        ),
        # Won't match the first MS, because there is no separator after MDX
        (
            "MS Sulfamethoxazole7 MS",
            "^(MDX|MS) {0,3}- {0,3}",
            "",
            "REGEX",
            "MS Sulfamethoxazole7 MS"
        ),
        # Create a task for PatientDrug that updates 'NS' or 'NSS' to 'saline solution' in meds column
        # It is more simply done in two steps: replace the NSS, then replace the NS.
        # Matches NSS
        ("NSS", "NSS", "saline solution", "BEGIN", "saline solution"),
        # But not NS
        ("NS", "NSS", "saline solution", "BEGIN", "NS"),
        # Matches NS
        ("NS", "NS", "saline solution", "BEGIN", "saline solution"),
        # And also NSS, so we must do them in the opposite order or with all in one
        ("NSS", "NS", "saline solution", "BEGIN", "saline solutionS"),
        # Match with additional text
        ("NSS + 20MEQ KCL 20 MEQ", "NSS", "saline solution", "BEGIN", "saline solution + 20MEQ KCL 20 MEQ"),
        # Change "#Basophils" to "Basophil count" - drop #, drop trailing 's', add 'count'.
        ("#Basolphils", "#Basolphils", "Basophil count", "BEGIN", "Basophil count"),
        # Do NOT match %Basophils (this needs a different rule)
        ("%Basolphils", "#Basolphils", "Basophil count", "BEGIN", "%Basolphils"),
        # Do NOT match %Basophils (this needs a different rule)
        ("Basolphils", "#Basolphils", "Basophil count", "BEGIN", "Basolphils"),
        # Do NOT match BASOPHILS ABSOLUTE (this needs a different rule)
        (
            "BASOPHILS ABSOLUTE",
            "#Basolphils",
            "Basophil count",
            "BEGIN",
            "BASOPHILS ABSOLUTE"
        ),
        # append ABC to text only if there is text
        ("text", "(.+)", "\\1ABC", "REGEX", "textABC"),
        # append ABC to text only if there is text
        ("", "(.+)", "\\1ABC", "REGEX", ""),
        # Test regex to not change a blank string
        ("", "(.+)", "\\1^^NDC", "REGEX", ""),  # leave blank string blank
        ("123", "(.+)", "\\1^^NDC", "REGEX", "123^^NDC"),  # but append if not blank
        # Test with the input being a list
        # "original_string, match, replacement, options, expected_result",
        (["111", "222"], "", "^^http://myurl", "END", ["111^^http://myurl", "222^^http://myurl"]),
        ([], "", "^^http://myurl", "END", []),  # handle an empty list.  List remains empty.
        (["111", "222", ""], "(.+)", "\\1^^http://myurl", "REGEX", ["111^^http://myurl", "222^^http://myurl", ""]),
        ("207Q00000X^Family Medicine Medical^http://nucc.org/provider-taxonomy",
         "^([^^]*)$", "\\1^tenant1", "REGEX", "207Q00000X^Family Medicine Medical^http://nucc.org/provider-taxonomy"),
        ("Family Medicine Medical", "^([^^]*)$", "\\1^tenant1", "REGEX", "Family Medicine Medical^tenant1"),
    ]
)
def test_replace_text_parameterized(
    original_string: str,
    match: str,
    replacement: str,
    options: str,
    expected_result: str,
):
    """
    Validates that replace_text works as expected.
    See comments next to parameterized values regarding each test.

    :param input_data_frame: The input data frame fixture, used as base
    :param expected_data_frame: The expected data frame, used as base
    :param original_string: the source string, which is added to the input dataframe for searching.
    :param match: the match string or regex used for searching.
    :param replacement: the replacement string or regex used for searching.
    :param options: options which may be used - REGEX, CASE_INSENSITIVE, BEGIN, END
    :param expected_result: the result string, which is added to the expected dataframe for final comparison.

    """
    input_df: DataFrame = DataFrame()
    input_df["testColumn"] = [original_string]
    expected_df: DataFrame = DataFrame()
    expected_df["testColumn"] = [expected_result]
    result: DataFrame = replace_text(
        input_df, "testColumn", match, replacement, options=options
    )
    assert_frame_equal(expected_df, result)


@ pytest.mark.parametrize("starting_index,ending_index", [
    (1, 5), (6, 10), (11, 15)])
def test_add_row_num(starting_index: int, ending_index: int):
    data = {"name": ["Fred", "Velma", "Shaggy", "Scooby", "Daphne"]}

    input_data_frame: DataFrame = DataFrame.from_dict(data)
    result: DataFrame

    result = add_row_num(input_data_frame, starting_index)
    actual_row_num_values = result["rowNum"].to_list()
    expected_row_num_values = list(range(starting_index, ending_index + 1))

    assert expected_row_num_values == actual_row_num_values


def test_change_case(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates that the change_case task updates data columns correctly

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame: The expected data frame, used for comparisons
    """

    # No casing input should equal no change
    result: DataFrame = change_case(input_data_frame, ["givenName", "familyName"])
    assert_frame_equal(expected_data_frame, result)

    # Conflicting casing input should equal no change
    result: DataFrame = change_case(input_data_frame, ["givenName", "familyName"], "UPPER LOWER")
    assert_frame_equal(expected_data_frame, result)

    # Test UPPER, use multiple columns
    expected_data_frame["givenName"] = ["THOMAS"]
    expected_data_frame["familyName"] = ["JONES"]
    result: DataFrame = change_case(input_data_frame, ["givenName", "familyName"], "UPPER")
    assert_frame_equal(expected_data_frame, result)

    # Test LOWER
    expected_data_frame["patientId"] = ["mrn1234"]
    result: DataFrame = change_case(input_data_frame, ["patientId"], "LOWER")
    assert_frame_equal(expected_data_frame, result)


def test_compare_to_date_all_defaults(input_data_frame: DataFrame, expected_data_frame: DataFrame):
    """
    Validates that the change_case task updates data columns correctly

    :param input_data_frame: The input data frame fixture
    :param expected_data_frame: The expected data frame, used for comparisons
    """
    input_data_frame["testDateColumn"] = ["2021-10-26T17:08:00+00:00"]
    expected_data_frame["testDateColumn"] = ["2021-10-26T17:08:00+00:00"]
    expected_data_frame["testBooleanCompare"] = ["TRUE"]
    result: DataFrame = compare_to_date(
        input_data_frame, "testDateColumn", "testBooleanCompare"  # TODAY, DATE_OR_BEFORE, TRUE, FALSE are defaulted
    )
    assert_frame_equal(expected_data_frame, result)


# Today's date used for paremetrized test below
todays_date_iso_string = date.today().isoformat()


@ pytest.mark.parametrize(
    "input_column_value, compare_date, comparison, expected_result",
    [
        # Test logic and default true and false values.=
        ("2021-10-26T17:08:00+00:00", "TODAY", "DATE_OR_BEFORE", "TRUE"),
        ("2021-10-26T17:08:00+00:00", "TODAY", "LE", "TRUE"),
        ("2021-10-26T17:08:00+00:00", "TODAY", "DATE_OR_AFTER", "FALSE"),
        ("2021-10-26T17:08:00+00:00", "TODAY", "GE", "FALSE"),
        (todays_date_iso_string, "TODAY", "EQUALS", "TRUE"),
        (todays_date_iso_string, "TODAY", "DATE_OR_BEFORE", "TRUE"),
        (todays_date_iso_string, "TODAY", "DATE_OR_AFTER", "TRUE"),
        (todays_date_iso_string, "TODAY", "AFTER_DATE", "FALSE"),
        (todays_date_iso_string, "TODAY", "BEFORE_DATE", "FALSE"),
        (todays_date_iso_string, "TODAY", "NOT_EQUAL", "TRUE"),
        (todays_date_iso_string, '2021-10-26', "AFTER_DATE", "TRUE"),
        (todays_date_iso_string, '2021-10-26', "DATE_OR_BEFORE", "FALSE"),
        (todays_date_iso_string, '2021-10-26', "DATE_OR_AFTER", "TRUE"),
        ("2021-10-26T17:08:00+00:00", "2021-10-26", "DATE_OR_BEFORE", "TRUE"),
        ("2021-10-26T17:08:00+00:00", "10-26-2021", "EQ", "TRUE"),
    ])
def test_compare_to_date_paramterized(
    input_data_frame: DataFrame,
    expected_data_frame: DataFrame,
    input_column_value,
    compare_date,
    comparison,
    expected_result
):
    """
    Validates that compare_to_date works as expected.
    See comments next to parameterized values regarding each test.

    :param input_data_frame: The input data frame fixture, used as base
    :param expected_data_frame: The expected data frame, used as base
    :param input_column_value: the value to be inserted into the data_frame, similar to an original column value.
    :param compare_date: The date to compared to
    :param comparison: a string indicating the comparison to be used
    :param expected_result: the result string ("TRUE" of "FALSE"), which is added to the expected dataframe.
    """
    input_data_frame["testDateColumn"] = [input_column_value]
    expected_data_frame["testDateColumn"] = [input_column_value]
    expected_data_frame["testTargetColumn"] = [expected_result]
    result: DataFrame = compare_to_date(
        input_data_frame, "testDateColumn", "testTargetColumn", compare_date, comparison
    )
    assert_frame_equal(expected_data_frame, result)


@ pytest.mark.parametrize(
    "input_column_value, compare_date, comparison, true_string, false_string, expected_result",
    [
        # test other scenarios with true and false output mappings
        ("2021-10-26T17:08:00+00:00", "10-26-2021", "EQ", "same", "different", "same"),
        ("2021-10-26T17:08:00+00:00", "TODAY", "DATE_OR_BEFORE", "completed", "not-done", "completed"),
        ("2021-10-26T17:08:00+00:00", "TODAY", "AFTER_DATE", "future", "past", "past"),
        ("2033-10-26T17:08:00+00:00", "TODAY", "DATE_OR_BEFORE", "completed", "not-done", "not-done")
    ])
def test_compare_to_date_with_mapped_true_false_paramterized(
    input_data_frame: DataFrame,
    expected_data_frame: DataFrame,
    input_column_value,
    compare_date,
    comparison,
    true_string,
    false_string,
    expected_result
):
    """
    Validates that compare_to_date works as expected.
    See comments next to parameterized values regarding each test.

    :param input_data_frame: The input data frame fixture, used as base
    :param expected_data_frame: The expected data frame, used as base
    :param input_column_value: the value to be inserted into the data_frame, similar to an original column value.
    :param compare_date: The date to compared to
    :param comparison: a string indicating the comparison to be used
    :param true_string: a string put in the result if the comparison is True
    :param true_string: a string put in the result if the comparison is False
    :param expected_result: the result string, which is added to the expected dataframe.
    """
    input_data_frame["testDateColumn"] = [input_column_value]
    expected_data_frame["testDateColumn"] = [input_column_value]
    expected_data_frame["testTargetColumn"] = [expected_result]
    result: DataFrame = compare_to_date(
        input_data_frame, "testDateColumn", "testTargetColumn", compare_date, comparison, true_string, false_string
    )
    assert_frame_equal(expected_data_frame, result)


def test_convert_to_list():
    """
    # Validates that the convert_to_list task updates data columns correctly

    # :param input_data_frame: The input data frame fixture
    # :param expected_data_frame: The expected data frame, used for comparisons
    """
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["111,222,333,444"]
    expected_df["test_column"] = [["111", "222", "333", "444"]]
    actual = convert_to_list(
        input_df,
        "test_column",
        ','
    )
    assert_frame_equal(expected_df, actual)

    # Test with embedded spaces.  Trim contents.
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["AAA  , BBB, CCC , DDD "]
    expected_df["test_column"] = [["AAA", "BBB", "CCC", "DDD"]]
    actual = convert_to_list(
        input_df,
        "test_column",
        ','
    )
    assert_frame_equal(expected_df, actual)

    # Test that default separator "," is used.
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["111,222,333,444"]
    expected_df["test_column"] = [["111", "222", "333", "444"]]
    actual = convert_to_list(
        input_df,
        "test_column"
    )
    assert_frame_equal(expected_df, actual)

    # Test multiple character separator
    # Test case checks multiple characters are not used individually as separators
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["111<=222<333=333"]
    expected_df["test_column"] = [["111", "222<333=333"]]
    actual = convert_to_list(
        input_df,
        "test_column",
        "<="
    )
    assert_frame_equal(expected_df, actual)

    # Test that separator which is not found creates a single entry in the list.
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["111,222,333,444"]
    expected_df["test_column"] = [["111,222,333,444"]]
    actual = convert_to_list(
        input_df,
        "test_column",
        "NO_MATCH"
    )
    assert_frame_equal(expected_df, actual)

    # Test that separator of empty string creates a single entry in the list.
    input_df: DataFrame = DataFrame()
    expected_df: DataFrame = DataFrame()
    input_df["test_column"] = ["111,222,333,444"]
    expected_df["test_column"] = [["111,222,333,444"]]
    actual = convert_to_list(
        input_df,
        "test_column",
        ""
    )
    assert_frame_equal(expected_df, actual)


@ pytest.mark.parametrize("source_columns, input_output_list, expected_output_list, remove_duplicates", [
    # Add first 2 columns to result.  Result is empty before this call.
    (["input1", "input2"], None, [["111^^NDC", "222^^RxNorm"]], False),
    # Add a column to an entry which already has 2 entries
    (["input3"], [["111^^NDC", "222^^RxNorm"]], [["111^^NDC", "222^^RxNorm", "333^^LOINC"]], False),
    # Tests having a list in the source column
    (["input4"], [["111^^NDC", "222^^RxNorm"]], [["111^^NDC", "222^^RxNorm", "444^^mysys", "^desc-only^mysys"]], False),
    # Add a column which is a duplicate of an existing entry, with discard option.
    (["input3"], [["111^^NDC", "222^^RxNorm", "333^^LOINC"]], [["111^^NDC", "222^^RxNorm", "333^^LOINC"]], True),
    # Test including a column which has a None value - this will not be included
    (["input1", "input5"], [["333^^LOINC"]], [["111^^NDC", "333^^LOINC"]], True),

])
def test_append_list(source_columns: List[str],
                     input_output_list: List,
                     expected_output_list: List,
                     remove_duplicates: bool):
    """
    Validates that the append_list task updates data columns correctly

    :param source_columns: The columns
    :param input_output_list: The fixture used to configure the input DataFrame's output list column.
    :param expected_output_list: The fixture used to define the expected "output list" for the DataFrame once the task
        has processed.
    :param remove_duplicates: maps to the append_list discard_if_duplicates parameter.
    """
    test_data = {
        "input1": ["111^^NDC"],
        "input2": ["222^^RxNorm"],
        "input3": ["333^^LOINC"],
        "input4": [["444^^mysys", "^desc-only^mysys"]],
        "input5": [None]
    }
    input_df: DataFrame = DataFrame(test_data)
    expected_df: DataFrame = DataFrame(test_data)

    # add default empty list if None is requested
    if input_output_list is None:
        input_output_list = [[] for _ in range(len(input_df))]
    input_df["output_list"] = input_output_list

    expected_df["output_list"] = expected_output_list

    actual = append_list(input_df, source_columns, "output_list", discard_if_duplicate=remove_duplicates)
    assert_frame_equal(expected_df, actual)


def test_append_list_multiple_rows():
    """
    Tests append list with an input data frame which contains multiple records
    """
    data = {
        "input1": ["111a^^NDC", "111b^^NDC", "111c^^NDC"],
        "input2": ["222a^^RxNorm", "222b^^RxNorm", "222c^^RxNorm"],
        "input3": ["333a^^LOINC", "333b^^LOINC", "333c^^LOINC"],
    }
    input_df: DataFrame = pd.DataFrame(data)
    expected_df: DataFrame = pd.DataFrame(data)
    expected_df["target"] = [
        ["111a^^NDC", "222a^^RxNorm"],
        ["111b^^NDC", "222b^^RxNorm"],
        ["111c^^NDC", "222c^^RxNorm"],
    ]

    actual: DataFrame = append_list(input_df, ["input1", "input2"], "target", discard_if_duplicate=False)
    assert_frame_equal(expected_df, actual)


def test_validate_value():
    data = {
        "input1": ["111a^^NDC", "111b^^NDCs", "111c^^NDC"],
        "input2": ["222a^^RxNorm", "222b^^RxNorm", "222c^^RxNorm"],
        "input3": ["333a^^LOINC", "333b^^LOINC", "333c^^LOINC"],
    }
    input_df: DataFrame = pd.DataFrame(data)
    actual = validate_value(input_df, 'input1', '111.*NDC$', "FailedToMatch")
    assert actual["input1"][0] == input_df["input1"][0]
    assert actual["input1"][2] == input_df["input1"][2]
    assert actual["input1"][1] == "FailedToMatch"


def test_join_data():
    data = {
        "firstname": ["patient1", "patient2", "patient3"],
        "MRN": ["111a^^NDC", "111b^^NDC", "111c^^NDC"],
    }
    input_df: DataFrame = pd.DataFrame(data)
    secondary_file = os.path.join(resources_directory, 'csv', 'patient-lastnames.csv')
    
    actual = join_data(input_df, secondary_file, 'left', 'MRN')
    assert actual['lastname'][0] == 'last1'
    assert math.isnan(actual['lastname'][1])
    assert actual['lastname'][2] == 'last3'