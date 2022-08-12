import os
from typing import Any, Dict, Generator, List, Optional, Tuple

import pandas as pd
from fhir.resources.meta import Meta
from numpy import integer
from pandas import DataFrame, Series

from linuxforhealth.csvtofhir import support
from linuxforhealth.csvtofhir.config import ConverterConfig, get_converter_config
from linuxforhealth.csvtofhir.fhirrs import meta
from linuxforhealth.csvtofhir.fhirrs.converter import convert_to_fhir
from linuxforhealth.csvtofhir.model.contract import (DataContract, FileDefinition,
                                                     GeneralSection, Task, load_data_contract)
from linuxforhealth.csvtofhir.pipeline.operations import execute

logger = support.get_logger(__name__)


class ConverterDefinitionLookupException(Exception):
    """
    Raised when the converter is unable to locate a file definition within the mapping resource.
    """

    pass


def validate_contract() -> DataContract:
    """
    Validates the converter's data contract
    :return: the DataContract model
    :raise: FileNotFoundError if the data contract configuration file is not found.
    :raise ValidationError if the data contract is not valid.
    """
    config = get_converter_config()

    if not os.path.exists(config.configuration_path):
        msg = f"Unable to load Data Contract configuration from {config.configuration_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    contract: DataContract = load_data_contract(config.configuration_path)
    return contract


def _create_processing_tasks(general: GeneralSection,
                             file_definition: FileDefinition,
                             file_path: str) -> List[Task]:
    """
    Creates the processing tasks used to transform source CSV data to an internal representation within a DataFrame.

    Processing tasks configured include:
    - copy_columns: Copies the column used for the group by key
    - add_constants: Adds fields from general into the DataFrame as columns
    - fileDefinitions.tasks: The tasks from the DataContract configuration

    add_row_num and set_nan_to_none tasks are configured by default

    :param general: The DataContract general section.
    :param file_definition: A DataContract FileDefinition
    :param file_path: The current file path
    :return:
    """
    # default tasks included in processing
    processing_tasks: List[Task] = [Task(name="add_row_num", params={"starting_index": 1}),
                                    Task(name="set_nan_to_none"),
                                    Task(name="remove_whitespace_from_columns")]

    # copy the column to be used as the groupBy key
    add_group_by_task = Task(
        name="copy_columns",
        params={
            "columns": [file_definition.groupByKey],
            "target_column": "groupByKey"})
    processing_tasks.append(add_group_by_task)

    # additional fields (general and constants) are applied to each row
    additional_fields = general.dict(exclude_none=True, exclude_unset=True)
    additional_fields["filePath"] = file_path
    additional_fields["configResourceType"] = file_definition.resourceType

    # create tasks to add the constant additional fields to each row
    additional_field_tasks = [
        Task(name="add_constant", params=dict(name=k, value=v))
        for k, v in additional_fields.items()
    ]
    processing_tasks.extend(additional_field_tasks)
    processing_tasks.extend(file_definition.tasks)

    return processing_tasks


def convert(file_path: str) -> Generator[Tuple[Any, str, List[str]], None, None]:
    """
    Converts file-based CSV records to FHIR Resources.

    Conversions are configured using a DataContract which in turn contains FileDefinitions. A single FileDefinition
    is used to define the CSV -> FHIR conversion process. CSV files are mapped to a FileDefinition using the CSV file
    name.

    Conversion occurs per row, converting a single CSV to one or more FHIR resources. Results are "yielded" to ensure
    a lower memory footprint. Each result is a tuple containing the following:

    - processing_exception: Contains the exception, if any, which occurred while processing the data record.
    - group_by_key: An identifier used to group converted FHIR resource(s) together.
    - fhir_resources: A list of JSON (string) converted FHIR resource(s).

    :param file_path: The path to the CSV file.
    :return: Generator yielding a tuple containing: processing errors (optional),  grouping key, and FHIR resources
    :raise: ConverterDefinitionLookupException if a FileDefinition cannot be found for the CSV file_path
    """

    def _append_row_num_to_file_meta(resource_meta: Meta, num: integer) -> Meta:
        """
        Appends the row number to the file name in source-file-id in the Meta

        :param resource_meta: the meta to add the row number to it's source-file-id
        :param num: the number of the source row
        :return: updated Meta
        """
        for extension in resource_meta.extension:
            if extension.url is not None and "source-file-id" in extension.url:
                # Meta is reused, so remove any existing num data before adding current num
                extension.valueString = extension.valueString.split(":")[0] + ":" + str(num).zfill(5)
                break
        return resource_meta

    def _convert_row_to_fhir(row: pd.Series) -> Tuple[Any, str, List[str]]:
        """
        A closure over the `resource_meta` for converting a DataFrame row into
        FHIR resources.

        :param row: The source row
        :return: List of converted FHIR Resources
        """
        try:
            processing_exception: Optional[Exception] = None
            result: List[str] = []
            log_message = (f"Converting row {row.rowNum} groupByKey={row.groupByKey} file_path={row.filePath} " +
                           "resourceType={row.configResourceType}")
            logger.debug(log_message)
            result = convert_to_fhir(
                row.groupByKey,
                row.to_dict(),
                _append_row_num_to_file_meta(
                    resource_meta,
                    row.rowNum))
        except Exception as ex:
            logger.error(f"Convert failed with {ex.__class__.__name__} Error")
            processing_exception = ex

        return processing_exception, row.groupByKey, result

    # load DataContract and FileDefinition
    contract: DataContract = validate_contract()

    file_name = os.path.basename(file_path)
    file_definition_lookup = os.path.splitext(file_name)[0]
    file_definition: Optional[FileDefinition] = None

    for k, v in contract.fileDefinitions.items():
        if k.lower() in file_definition_lookup.lower():
            file_definition = v
            break

    if not file_definition:
        msg = f"Unable to load definition {file_definition} for {file_definition_lookup}"
        logger.error(msg)
        raise ConverterDefinitionLookupException(msg)

    resource_meta: Meta = meta.create_meta(file_name, file_definition.resourceType, contract.general.dict())
    chunk_tasks = _create_processing_tasks(contract.general, file_definition, file_path)
    csv_reader_params = build_csv_reader_params(get_converter_config(), contract.general, file_definition)

    with pd.read_csv(file_path, **csv_reader_params) as buffer:
        for chunk in buffer:

            chunk: DataFrame = execute(chunk_tasks, chunk)

            # increment the source row number for the next chunk/buffer processed
            # add_row_num is the first task in the list
            starting_row_num = chunk["rowNum"].max() + 1
            chunk_tasks[0] = Task(name="add_row_num", params={"starting_index": starting_row_num})

            chunk: Series = chunk.apply(_convert_row_to_fhir, axis=1)

            for processing_exception, group_by_key, fhir_resources in chunk:
                yield processing_exception, group_by_key, fhir_resources


def build_csv_reader_params(
    config: ConverterConfig,
    general_section: GeneralSection,
    file_definition: FileDefinition,
) -> Dict[str, Any]:
    """
    Builds the Pandas CSV Reader parameters based on converter and file definition settings.

    :param config: The converter configuration
    :param general_section: The DataContract general section/settings
    :param file_definition: The current file definition
    :return: Dictionary of settings
    """

    params = {
        "chunksize": config.csv_buffer_size,
        "delimiter": file_definition.valueDelimiter
    }

    if file_definition.convertColumnsToString:
        params["dtype"] = str

    if general_section.emptyFieldValues:
        params["na_values"] = general_section.emptyFieldValues

    if file_definition.headers:
        params["header"] = None  # All lines in the file are data lines
        header_columns = []

        # headers contain comments and are List[Dict[str, str]]
        if isinstance(file_definition.headers[0], dict):
            for item in file_definition.headers:
                header_columns.extend(item.keys())
        else:
            # headers are List[str]
            header_columns.extend(file_definition.headers)

        params["names"] = header_columns

    logger.debug(f"Parsed parameters for CSV Reader {params}")

    return params
