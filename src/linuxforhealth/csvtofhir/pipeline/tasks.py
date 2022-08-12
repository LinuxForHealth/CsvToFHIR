import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Union
import operator
import numpy as np
import pandas as pd
from dateutil.parser import parse
from pandas import DataFrame, Series

from linuxforhealth.csvtofhir import support
from linuxforhealth.csvtofhir.config import get_converter_config
from linuxforhealth.csvtofhir.support import read_csv
# Do not remove, required for _build_status_history task
from linuxforhealth.csvtofhir.model.csv.encounter import EncounterStatusHistoryEntry

logger = support.get_logger(__name__)


class TaskException(Exception):
    """
    Raised when a task is unable to execute.
    """
    pass


def _matched_columns(
    columns: List[str],
    data_frame: DataFrame
) -> List[str]:
    """
    Return a matching set of column names from a DataFrame.
    :param columns: The column names to search for
    :param data_frame: The DataFrame to search
    :return: List containing the matching column names
    """
    df_columns: List[str] = data_frame.columns.to_list()
    return [c for c in columns if c in df_columns]


def add_constant(
    data_frame: DataFrame,
    name: str,
    value: Any
) -> DataFrame:
    """
    Adds a constant value as a column in a DataFrame.
    The column is appended to each DataFrame row

    :param data_frame: The input DataFrame
    :param name: The constant name, used as the DataFrame column name.
    :param value: The constant value
    :return: The updated DataFrame.
    """
    if name in data_frame.columns.to_list():
        logger.warning(f"Unable to add constant. Column {name} already exists")
        return data_frame

    if isinstance(value, list):
        data_frame[name] = pd.Series([value]) * len(data_frame)
    else:
        data_frame[name] = value
    return data_frame


def copy_columns(
    data_frame: DataFrame,
    columns: List[str],
    target_column: str,
    value_separator=" "
):
    """
    Copies one or more source columns to a target column.

    :param data_frame: The input data frame
    :param columns: The column(s) to copy
    :param target_column: The copy target
    :param value_separator: The value used to join source column values in the target column. Defaults to a " "
    :return: the updated data frame
    """
    if value_separator is None:
        value_separator = " "

    mc = _matched_columns(columns, data_frame)
    logger.debug(f"{len(mc)} matching columns")
    if len(mc) == 0:
        logger.warning("No matching columns")

    # Local lambda function which converts an array of objects to an array of strings
    # Handles special case where None becomes empty string
    def _string_or_empty_for_none(aa):
        b = []
        for a in aa:
            b.append(str(a) if a is not None else "")
        return b

    if mc:
        data_frame[target_column] = data_frame[mc].apply(
            lambda x: value_separator.join(_string_or_empty_for_none(x.values)), axis=1
        )

    return data_frame


def filter_to_columns(
    data_frame: DataFrame,
    source_column: str,
    target_columns: List[str],
    filters: List[List[str]]
):
    """
    Filters (partitions) a source column into multiple target columns.
    A list of matching values is input for each target column.
    If all of the columns have a matching value list, any unmatched values are discarded.
    If the matching value list is omitted for the final column, any unmatched values are placed there.
    Python None is placed in cells where there is no match.

    :param data_frame: The input data frame
    :param source_column: The column to copy and filter
    :param target_columns: A list of target columns
    :param filters: A list of matching value lists for each column.  A filter for the last column is optional.
    :return: The updated data frame
    """

    existing_columns = _matched_columns(target_columns, data_frame)
    if existing_columns:
        logger.warn(
            f"Unable to filter columns. New columns: {existing_columns} exist within the data frame"
        )
        return data_frame

    if len(target_columns) != len(filters) and len(target_columns) != len(filters) + 1:
        logger.warn(
            "Unable to filter columns. New column number must be equal or +1 to filter number"
        )
        return data_frame

    if source_column not in data_frame.columns.to_list():
        # continue the pipeline
        return data_frame

    def _filter_target(x: str, filter: set, standard_or_reverse: bool):
        # This tricky logic allows us to reverse filter (anti-filter) when False
        # Logically equvalent to: if x <not> in filter
        if (x in filter) is standard_or_reverse:
            return x
        return None

    STANDARD_FILTER = True
    REVERSE_FILTER = False
    # match each filter to a new filtered column and filter (standard)
    for idx, filter in enumerate(filters):
        data_frame[target_columns[idx]] = np.vectorize(_filter_target)(
            data_frame[source_column], set(filter), STANDARD_FILTER)

    # if there is an extra column, it will collect leftovers (reverse filter of all other filters)
    if (len(target_columns) > len(filters)):
        anti_filter = set().union(*filters)  # combine all filters to anti-filter
        target_column_index = len(target_columns) - 1  # last new column
        data_frame[target_columns[target_column_index]] = np.vectorize(
            _filter_target)(data_frame[source_column], anti_filter, REVERSE_FILTER)

    return data_frame


def find_not_null_value(data_frame: DataFrame, columns: List[str], target_column: str) -> DataFrame:
    """
    Sets value from iterating input columns looking for first not null value.

    :param data_frame: The input data frame
    :param columns: The column(s) to inspect / copy from if non-null
    :param target_column: Column name to place the first not null value into
    :return: the updated data frame
    """
    mc = _matched_columns(columns, data_frame)
    logger.debug(f"{len(mc)} matching columns")
    if len(mc) == 0:
        logger.warning("No matching columns")
    else:
        data_frame = set_nan_to_none(data_frame)

        # bfill(axis=1) --> back fills any None values from value in the next column
        #                   (axis=1 indicates it is working on columns)
        # iloc[:,0] --> slices the data taking the first column which should have
        #               been 'backfilled' to the first non null value
        data_frame[target_column] = data_frame[mc].bfill(axis=1).iloc[:, 0]

    return data_frame


def format_date(
    data_frame: DataFrame,
    columns: List[str],
    date_format="%Y-%m-%d"
) -> DataFrame:
    """
    Formats date string values within a DataFrame column to a target date format.

    :param data_frame: The input DataFrame
    :param columns: The column names to update
    :param date_format: The target date format. Defaults to %Y-%m-%d
    :return: The updated DataFrame
    """
    target_columns = _matched_columns(columns, data_frame)
    logger.debug(f"{len(target_columns)} matching columns")
    if len(target_columns) == 0:
        logger.warning("No matching columns")

    for c in target_columns:
        data_frame[c] = data_frame[c].apply(lambda x: parse(x).strftime(date_format))

    return data_frame


def rename_columns(data_frame: DataFrame, column_map: Dict[str, str]) -> DataFrame:
    """
    Renames a DataFrame's columns using a column_map, or dictionary.

    :param data_frame: The input DataFrame
    :param column_map: The dictionary used to map current column names to desired column names.
    :return: the updated DataFrame
    """
    matched_columns: List[str] = _matched_columns(list(column_map.keys()), data_frame)
    updated_map = {k: v for k, v in column_map.items() if k in matched_columns}
    if not updated_map:
        logger.warning("No matched columns")
        return data_frame
    else:
        updated_data_frame = data_frame.rename(columns=updated_map)
        return updated_data_frame


def set_nan_to_none(data_frame: DataFrame):
    """
    Updates NaN values in DataFrame columns to Python's None type.
    This task is included by default with the CSVToFHIR convert operation.
    :param data_frame: The input DataFrame.
    :return: The updated DataFrame
    """
    # sets NaN and Na values to None
    updated_data_frame = data_frame.replace(np.nan, None)
    return updated_data_frame


def map_codes(
    data_frame: DataFrame,
    code_map: Union[Dict[str, Dict], Dict[str, str]]
) -> DataFrame:
    """
    Maps code values from a source to target value, within a DataFrame.
    The mapping process supports a "default" key in the code_map which is used to identify a default value to use
    if a mapping is not found.

    :param data_frame: The input DataFrame
    :param code_map: The dictionary containing the mapping values or a filename that contains the mappings.
    :return: The updated DataFrame
    """
    # Get the directory where the data contract is located.
    file_directory = os.path.dirname(get_converter_config().configuration_path)

    # if the code_map value is a file load it and replace the file with the resolved csv dict
    for k, v in code_map.items():
        if isinstance(v, str):
            filepath = os.path.join(file_directory, v)
            code_map_dict = read_csv(filepath)
            code_map[k] = code_map_dict

    matched_columns: List[str] = _matched_columns(list(code_map.keys()), data_frame)
    logger.debug(f"{len(matched_columns)} matching columns")
    if len(matched_columns) == 0:
        logger.warn("No matching columns")

    for c in matched_columns:
        map_values = code_map[c]
        data_frame[c] = data_frame[c].transform(
            lambda x: map_values.get(x, map_values.get("default", x))
        )

    return data_frame


def split_row(
    data_frame: DataFrame,
    columns: List[str],
    split_column_name: str,
    split_value_column_name: str
) -> DataFrame:
    """
    Splits DataFrame rows on the specified column(s) creating two new columns for the column name and value.

    :param data_frame: The input DataFrame
    :param columns: The column(s) to split on
    :param split_column_name: The column name used for the split column
    :param split_value_column_name: The column name for this split column value
    :return: the updated DataFrame
    """
    matched_columns = _matched_columns(columns, data_frame)
    logger.debug(f"{len(matched_columns)} matching columns")
    if len(matched_columns) == 0:
        logger.warning("No matching columns")

    if matched_columns:
        melt_vars: List[str] = [
            c for c in data_frame.columns.to_list() if c not in matched_columns
        ]
        updated_data_frame: DataFrame = pd.melt(
            data_frame,
            id_vars=melt_vars,
            var_name=split_column_name,
            value_name=split_value_column_name,
        )
        return updated_data_frame

    return data_frame


def conditional_column(
    data_frame: DataFrame,
    source_column: str,
    condition_map: Union[Dict, str],
    target_column: str
) -> DataFrame:
    """
    Creates a new column, a conditional column, by mapping the values from a "source" column to a target value, using
    a dictionary.
    If mapping not found:
          "default": <value> will be used if present
          otherwise leave existing value from source

    :param data_frame: The input DataFrame
    :param source_column: The source column for the new conditional column
    :param condition_map: Maps values from the source column to the desired target values or a filename
     that contains the mappings.
    :param target_column: The new/target column
    :return: The updated DataFrame
    """
    # Get the directory where the data contract is located.
    file_directory = os.path.dirname(get_converter_config().configuration_path)

    # if the code_map value is a file load it and replace the file with the resolved csv dict
    if isinstance(condition_map, str):
        filepath = os.path.join(file_directory, condition_map)
        code_map_dict = read_csv(filepath)
        condition_map = code_map_dict

    if source_column in data_frame.columns.to_list():
        data_frame[target_column] = data_frame[source_column].apply(
            lambda x: condition_map.get(x, condition_map.get("default", x))
        )

    return data_frame


def conditional_column_update(
    data_frame: DataFrame,
    source_column: str,
    condition_map: Union[Dict, str],
    target_column: str
) -> DataFrame:
    """
    Updates existing column, by mapping the values from a "source" column to a target value,
    using a dictionary.

    If mapping not found:
          "default": <value> will be used if present
          otherwise leave value in the existing target_column as-is

    :param data_frame: The input DataFrame
    :param source_column: The source column to use for the mapping
    :param condition_map: Maps values from the source column to the desired target values or a filename
     that contains the mappings.
    :param target_column: The existing target column to update
    :return: The updated DataFrame
    """
    # Get the directory where the data contract is located.
    file_directory = os.path.dirname(get_converter_config().configuration_path)

    # if the code_map value is a file load it and replace the file with the resolved csv dict
    if isinstance(condition_map, str):
        filepath = os.path.join(file_directory, condition_map)
        code_map_dict = read_csv(filepath)
        condition_map = code_map_dict

    def _conditional_map(source_value: str, condition_map: dict, target_value: str) -> Union[None, str]:
        return condition_map.get(source_value, condition_map.get("default", target_value))

    if source_column in data_frame.columns.to_list():
        str_array = np.vectorize(_conditional_map)(
            data_frame[source_column],
            condition_map,
            data_frame[target_column]
        )
        data_frame[target_column] = _clean_vectorized_data(str_array)

    return data_frame


def conditional_column_with_prerequisite(
    data_frame: DataFrame,
    source_column: str,
    condition_map: Union[Dict, str],
    target_column: str,
    prerequisite_column: str,
    prerequisite_match: str = None
) -> DataFrame:
    """
    If a prerequisite column is present with a matching regex value, create a new column or updates existing column,
    by mapping the values from a "source" column to a target value, using a dictionary.
    If the prerequisite is not met, the target column is left as is
    If mapping not found:
          "default": <value> will be used if present
          otherwise leave existing value from source

    :param data_frame: The input DataFrame
    :param source_column: The source column for the new conditional column
    :param condition_map: Maps values from the source column to the desired target values or a filename that contains
                          the mappings.
    :param target_column: The new/target column
    :param prerequisite_column: a column which must contain a value specified before the conditional is processed
    :param prerequisite_match: pattern that must be matched in the prerequisite column. None (default) matches to None,
    otherwise the match value is treated as regex.

    Notes: The JSON of data-contracts does not allow None.  Use null in the JSON data-contract, and it is converted
    to None in the python task processing.

    :return: The updated DataFrame
    """
    # Get the directory where the data contract is located.
    file_directory = os.path.dirname(get_converter_config().configuration_path)

    # if the code_map value is a file load it and replace the file with the resolved csv dict
    if isinstance(condition_map, str):
        filepath = os.path.join(file_directory, condition_map)
        code_map_dict = read_csv(filepath)
        condition_map = code_map_dict

    def _conditional_map_after_prereq(source_value: str, condition_map: dict,
                                      target_value: str, prereq_value, prereq_match) -> Union[None, str]:
        matched = False
        # If no source_value, then treat as no match
        if source_value is None:
            matched = False
        # Special cases for matching empty fields
        # Check for empty match value
        elif prereq_match is None:
            matched = prereq_value is None
        # Check empty prereq_value: if None and prereq_match is not None (previous step) matched is false
        elif prereq_value is None:
            matched = False
        else:  # assume regex
            matched = re.search(prereq_match, prereq_value)

        # Process depending on whether matched.
        if matched:
            return condition_map.get(source_value, condition_map.get("default", target_value))
        else:
            return target_value

    if source_column in data_frame.columns.to_list():
        str_array = np.vectorize(_conditional_map_after_prereq)(
            data_frame[source_column],
            condition_map,
            data_frame[target_column],
            data_frame[prerequisite_column],
            prerequisite_match)
        data_frame[target_column] = _clean_vectorized_data(str_array)

    return data_frame


def _clean_vectorized_data(str_array):
    # vectorize has the bad side effect of assuming everything should be a string.
    # This converts each None back from string to a None object in the result
    # array, and places in the data_frame column.
    mixed_array = []
    for el in str_array:
        mixed_array.append(None) if el == 'None' else mixed_array.append(el)
    return mixed_array


def build_object_array(
    data_frame: DataFrame,
    entry_class: str,
    target_column: str,
    entries: Union[Dict, str],
) -> DataFrame:
    """
    Builds an array of a string representation of an object.
    Typical output is something like this:
        ["<field1>^<field2>^<field3>", "<field1>^<field2>^<field3>"]
        (fields (and order) come from the specified entry_class pydantic model)

    :param data_frame: The input DataFrame
    :param entry_class: The class name of the pydantic model that will be used.
    :param entries: An array of string objects.
        Example: [{"foo1":"bar1", "foo2":"bar2"},{"foo3":"bar3", "foo4":"bar4"}]
    :param target_column: The new/target column
    :return: The updated DataFrame
    """

    if target_column not in data_frame.columns:
        data_frame[target_column] = [[] for _ in range(len(data_frame))]
    else:
        # clean up target
        # target column exists - set None values to []
        data_frame[target_column] = data_frame[target_column].apply(lambda df: [] if df is None else df)

    # pass in the fields we need in the _build_status_history function
    variable_list = []
    for entry in entries:
        for key in entry:
            value = entry[key]
            if value and value[0] == "$":
                variable_list.append(value[1:len(value)])
    variable_list.append(target_column)

    # remove duplicates
    variable_list = list(set(variable_list))

    data_frame[target_column] = data_frame[variable_list].apply(
        _build_status_history, axis=1, args=(entry_class, entries)  # passes value in data frame as first parm
    )

    return data_frame


def _build_status_history(
        column_value: Union[Dict, str],
        entry_class: str,
        entries: List[dict],
):
    entry_klass = globals()[entry_class]
    built_string_list = []
    for incoming_entry in entries:
        built_string = ""
        model_fields = list(entry_klass.__fields__)
        # pull the values in the order they appear in the EncounterStatusHistoryEntry class
        for i in range(len(model_fields)):
            value = incoming_entry[model_fields[i]]
            # if the value is a variable
            if value and value[0] == "$":
                # strip of the $ to get the var name
                var_name = value[1:len(value)]
                # get the value from existing data
                value = column_value[var_name]
            built_string += str(value) + "^"
        # remove extra ^ at the end
        built_string = built_string[0:len(built_string) - 1]
        built_string_list.append(built_string)

    return built_string_list


def split_column(
    data_frame: DataFrame,
    column_name: str,
    new_column_names: List[str],
    delimiter: Optional[str] = None,
    indices: Optional[List[List[int]]] = None
) -> DataFrame:
    """
    Splits a single column's values into new column(s) using either delimiter or starting/ending indices.

    The delimiter parameter is used when a column's values are parsed using a single delimiter character such as ","
    or "|".  If more columns to create than are found delimited substrings, unfilled columns contain None.

    The indices parameter is a List containing starting/ending indices:

    [[0, 5], [5, 10]]
    [[0, 5], [5]]

    Note that the ending index may be omitted so that the remainder of the string is selected

    The starting and ending indices are zero based and use the same boundary conditions as Python string slicing.

    :param data_frame: The input DataFrame
    :param column_name: The source column name
    :param new_column_names: The new/target columns added to the DataFrame
    :param delimiter: A delimiter character such as a "," or "|"
    :param indices: A List containing Lists of starting/ending indices.
    :return: the updated DataFrame
    :raise: ValueError if any of "new_columns" exist in the DataFrame or if an index boundary does not contain
     the correct number of entries.
    """
    existing_columns = _matched_columns(new_column_names, data_frame)
    if existing_columns:
        logger.warn(f"Unable to split columns. New columns: {existing_columns} exist within the data frame")
        return data_frame
    if column_name not in data_frame.columns.to_list():
        # continue the pipeline
        return data_frame

    source_column = data_frame[column_name]
    if delimiter:
        data_frame[new_column_names] = source_column.str.split(
            delimiter, expand=True).reindex(
            columns=range(len(new_column_names))).replace(np.nan, None)
    else:
        if len(indices) != len(new_column_names):
            msg = f"The number of index pairs {len(indices)} != number of new columns {len(new_column_names)}"
            raise ValueError(msg)

        for i, index_bounds in enumerate(indices):
            if len(index_bounds) == 0 or len(index_bounds) > 2:
                msg = f"Index boundaries may contain 1 or 2 elements. {index_bounds} is invalid."
                raise ValueError(msg)

            start_index = index_bounds[0]
            end_index = index_bounds[1] if len(index_bounds) == 2 else None
            data_frame[new_column_names[i]] = source_column.str[
                slice(start_index, end_index)
            ]

    return data_frame


def replace_text(
    data_frame: DataFrame,
    column_name: str,
    match: str,
    replacement: str,
    options: Optional[str] = ""
) -> DataFrame:
    """
    Replaces text found in each row of a DataFrame column.
    If the content of the column is a list, each item in the list is processed.

    :param data_frame: The input DataFrame
    :param column_name: The DataFrame column name.
    :param match: The string to match. Or pattern if REGEX option.
    :param replacement: The string to replace it with.  Or pattern if REGEX option.
    :param options: optional string of options, defaults to None, which is match anywhere, case sensitive
        BEGIN = match at the beginning of the string. Can be combined with CASE_INSENSITIVE and/or END.
        END = match at the end of the word. Can be combined with CASE_INSENSITIVE and/or BEGIN.
        CASE_INSENSITIVE = match without respect to case. Can be combined with BEGIN and/or END.
        REGEX = the match and the replacement are regex formulae. Supercedes all other options causing them to
         be ignored.
    :return: The updated DataFrame.
    """

    is_regex: bool = bool(options.upper().find("REGEX") > -1)
    case_insensitive: str = "(?i)" if options.upper().find('CASE_INSENSITIVE') > -1 else ""
    begin: str = "^" if options.upper().find('BEGIN') > -1 else ""
    end: str = "$" if options.upper().find('END') > -1 else ""

    regexs = []
    # If REGEX option, no other options are considered.
    if is_regex:
        regexs.append(match)
    else:
        # Build our regex. We run everything as a regex, because replace only operates on the complete string
        match_escaped = re.escape(match)
        if begin and end:
            # If *both* BEGIN *and* END, we need to do two calls, one with END and one with BEGIN.
            # Do END first as preprocess to the BEGIN which is handled in main processing.
            case_insensitive_endonly: str = "(?i)" if options.upper().find('CASE_INSENSITIVE') > -1 else ""
            regex_str_endonly = f"{case_insensitive_endonly}{match_escaped}{end}"
            regexs.append(regex_str_endonly)
            # regex for main processing does not consider end, because it was just handled.
            regexs.append(f"{case_insensitive}{begin}{match_escaped}")
        else:
            # Otherwise only one of (or neither) BEGIN and END are used, we can build the general regex
            regexs.append(f"{case_insensitive}{begin}{match_escaped}{end}")

    data_frame[column_name] = data_frame[column_name].apply(
        _run_regex, args=(regexs, replacement)  # passes value in data frame as first parm
    )

    return data_frame


def _run_regex(
    column_value: Union[str, list[str]],
    regexs: list[str],
    replacement: str
):
    # handle differently depending on whether a list or single value
    if _is_sequence(column_value):
        result_values = []
        for value in column_value:
            if value != 'None':  # can get a single array value of 'None', we do not want to preserve this
                new_value = value
                for regex in regexs:
                    new_value = re.sub(regex, replacement, new_value)
                result_values.append(new_value)
        return result_values
    else:
        # When value is None, always return None, don't attempt regex
        if column_value is None:
            return None
        if not column_value:
            column_value = ""
        new_value = column_value
        for regex in regexs:
            new_value = re.sub(regex, replacement, new_value)
        return new_value


def add_row_num(
    data_frame: DataFrame,
    starting_index: int = 1
) -> DataFrame:
    """
    Adds a row number column to the DataFrame.
    This task is included by default with the CSVToFHIR convert operation.

    :param data_frame: The input DataFrame
    :param starting_index: The starting value for the row number column. Defaults to 1.
    :return: The updated DataFrame
    """
    ending_index = len(data_frame) + starting_index
    index_values = list(range(starting_index, ending_index))
    data_frame["rowNum"] = index_values
    return data_frame


def remove_whitespace_from_columns(data_frame: DataFrame) -> DataFrame:
    """
    Strips white space from the start or end of the column names.
    :param data_frame: The input DataFrame.
    :return: The updated DataFrame
    """
    updated_data_frame = data_frame
    updated_data_frame.columns = data_frame.columns.str.strip()
    return updated_data_frame


def change_case(
    data_frame: DataFrame,
    columns: List[str],
    casing: Optional[str] = ""
) -> DataFrame:
    """
    Changes the case of all text of one or more source columns of a DataFrame.

    :param data_frame: The input DataFrame
    :param columns: A list of column names to change
    :param casing: string indicating case type
        UPPER = change all characters to upper-case
        LOWER = change all character to lower-case
        Note: omitting or setting more than one casing will result in NO CHANGE
    :return: The updated DataFrame.
    """
    make_upper: bool = bool(casing.upper().find("UPPER") > -1)
    make_lower: bool = bool(casing.upper().find("LOWER") > -1)
    if not casing or make_upper and make_lower:
        logger.warning(f'No changes because of casing parameters: "{casing}"')
        return data_frame

    target_columns = _matched_columns(columns, data_frame)
    logger.debug(f"{len(target_columns)} matching columns")
    if len(target_columns) == 0:
        logger.warning("No matching columns")

    for c in target_columns:
        if make_upper:
            data_frame[c] = data_frame[c].apply(lambda x: x.upper())
        if make_lower:
            data_frame[c] = data_frame[c].apply(lambda x: x.lower())

    return data_frame


def compare_to_date(
    data_frame: DataFrame,
    column: str,
    target_column: str,
    compare_date: Optional[str] = "TODAY",
    comparison: Optional[str] = "DATE_OR_BEFORE",
    true_string: Optional[str] = "TRUE",
    false_string: Optional[str] = "FALSE"
) -> DataFrame:
    """
    Creates a new target_column with mapped values for boolean comparison of the source column date
    compared to the compare_date.

    :param data_frame: The input DataFrame
    :param column: the source column with a date.  Empty date values will result in false.
    :param target_column: the target column to be created.
      Will contain true_string or false_string values based on comparison result.
    :param compare_date: date used for comparison to the date in column.
      A special value of "TODAY" if found will use today's date for comparison.
      Optional value.  If omitted, defaults to "TODAY".
    :param comparison: comparison between the compare date and the date in column.
      Optional.  If omitted, defaults to "DATE_OR_BEFORE".
      Valid values:
        DATE_OR_BEFORE or LE
        BEFORE_DATE or LT
        EQUALS or EQ
        AFTER_DATE or GT
        DATE_OR_AFTER or GE
        NOT_EQUALS or NE
    :param true_string: a string put in the result if the comparison is True. Optional. Defaults to "TRUE"
    :param false_string: a string put in the result if the comparison is False. Optional. Defaults to "FALSE"
    :return: The updated DataFrame.
    """
    if compare_date.upper().find("TODAY") > -1:
        date_compare_date = date.today()
    else:
        date_compare_date = parse(compare_date).date()

    if any(x in comparison.upper() for x in ['DATE_OR_BEFORE', 'LE']):
        comp = operator.le
    elif any(x in comparison.upper() for x in ['BEFORE_DATE', 'LT']):
        comp = operator.lt
    elif any(x in comparison.upper() for x in ['EQUALS', 'EQUAL', 'EQ']):
        comp = operator.eq
    elif any(x in comparison.upper() for x in ['DATE_OR_AFTER', 'GE']):
        comp = operator.ge
    elif any(x in comparison.upper() for x in ['AFTER_DATE', 'GT']):
        comp = operator.gt
    elif any(x in comparison.upper() for x in ['NOT_EQUALS', 'NOT_EQUAL', 'NE']):
        comp = operator.ne

    data_frame[target_column] = data_frame[column].apply(
        lambda d: true_string if d and comp(parse(d).date(), date_compare_date) else false_string
    )

    return data_frame


def convert_to_list(
    data_frame: DataFrame,
    column: str,
    separator: Optional[str] = ","
) -> DataFrame:
    """
    Separates the data of a column based on a separator character, and places the list into a new column.

    :param data_frame: The input DataFrame
    :param column: Column that will be converted to a list.  This is expected to be a string.
    :param separator: Character or string to split the column on to create list entries
    If not provided, separator defaults to "," (comma)
    If empty string '' provided, the entire contents of column are put as single entry in list.

    :return: The updated DataFrame.
    """
    # Special handling for empty string.  Just make a list of the value, unseparated.
    if len(separator) < 1:
        data_frame[column] = data_frame[column].apply(
            lambda x: [x]
        )
        return data_frame

    # Standard handling
    data_frame[column] = data_frame[column].apply(
        # Passes value in data frame as first parm.
        # Note comma is necessary for tuple conversion. (Otherwise the string is separated to characters.)
        _run_split, args=(separator,)
    )
    return data_frame


def _run_split(
    column_value: str,
    separator: str
):
    # When value is None, always return None, don't attempt split
    if column_value is None:
        return None
    else:
        value_list = column_value.split(separator)
        stripped_list = [x.strip() for x in value_list]
        return stripped_list


def _is_sequence(column_value) -> bool:
    """
    Returns True if a data frame column value is a sequence (list, Series, or set)
    """
    return type(column_value) in (list, Series, set)


def append_list(
    data_frame: DataFrame,
    source_columns: List[str],
    target_column: str,
    discard_if_duplicate: Optional[bool] = False
) -> DataFrame:
    """
    Separates the data of a column based on a separator character, and places the list into a new column.
    If the item already exists in the list, it will not be added.

    :param data_frame: The input DataFrame
    :param source_columns: Columns to add to the target column.  Columns should contain a string, or a list of strings.
    :param target_column: the column to add source_columns to. This column must be a list of strings.
    :param discard_if_duplicate:

    :return: The updated DataFrame.
    """
    # create a "tmp" column for a work-area
    data_frame["tmp"] = [[] for _ in range(len(data_frame))]

    try:
        # create the target column with default values, if it does not exist
        if target_column not in data_frame.columns:
            data_frame[target_column] = [[] for _ in range(len(data_frame))]
        else:
            # clean up target
            # target column exists - set None values to []
            data_frame[target_column] = data_frame[target_column].apply(lambda df: [] if df is None else df)
            # append existing target values to our tmp column
            # use list extend or append based on the target_columns datatype
            data_frame.apply(
                lambda x: x["tmp"].extend(
                    x[target_column]) if _is_sequence(
                    data_frame[target_column]) else x["tmp"].append(
                    data_frame[target_column]),
                axis=1)

        # copy source values to tmp column
        for col in source_columns:
            data_frame.apply(
                lambda x: x["tmp"].extend(x[col]) if _is_sequence(x[col]) else x["tmp"].append(x[col]),
                axis=1
            )
        # clean up None list entries
        data_frame["tmp"] = data_frame.apply(
            lambda x: [item for item in x["tmp"] if item is not None],
            axis=1
        )

        if discard_if_duplicate:
            data_frame[target_column] = data_frame.apply(lambda x: sorted(list(set(x["tmp"]))), axis=1)
        else:
            data_frame[target_column] = data_frame.apply(lambda x: sorted(list(x["tmp"])), axis=1)

    except Exception as ex:
        logger.error(f"An error occurred processing {ex}")
    finally:
        if "tmp" in data_frame.columns:
            data_frame.drop(["tmp"], axis=1, inplace=True)
    return data_frame
