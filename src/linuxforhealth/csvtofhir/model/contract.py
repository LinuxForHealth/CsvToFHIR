import json
import pytz
from enum import Enum
from inspect import Parameter, signature
from pydantic import Field, root_validator, validator
from typing import Any, Dict, List, Optional, Union
from fhir.resources.fhirtypesvalidators import MODEL_CLASSES

from linuxforhealth.csvtofhir.model.base import ImmutableModel
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def create_resource_list() -> List[str]:
    return [k.lower() for k in MODEL_CLASSES.keys()] + [
        "unstructured",
        "medication_use"
    ]


FHIR_RESOURCES = create_resource_list()


def is_required_parameter(p: Parameter) -> bool:
    """
    Filter function used in task validations, which returns True if a task parameter is required by the DataContract
    definition.
    A parameter is required if it is not the DataFrame parameter or a default parameter.
    :param p: Function parameter object
    :return: True if the parameter is required, otherwise False.
    """
    return p.name != "data_frame" and p.default == Parameter.empty


class DataStreamType(str, Enum):
    """
    Identifies the type of data stream used within the DataContract instance.
    """
    HISTORICAL = ("historical",)
    LIVE = "live"


class GeneralSection(ImmutableModel):
    """
    Contains general resource mapping configurations
    """
    timeZone: str = Field(description="Valid tz database/IANA values")
    tenantId: str = Field(description="The customer tenant id")
    assigningAuthority: Optional[str] = Field(
        description="The system of record, or issuer, for FHIR id and code values"
    )
    streamType: DataStreamType = Field(
        description="Indicates if the stream contains historical data or live (current) data",
        default=DataStreamType.LIVE
    )
    emptyFieldValues: Optional[List[str]]

    @validator("timeZone")
    def validate_time_zone(cls, v):
        """
        Validates that the time zone field contains a valid TZ Database/ICANN value
        :param v: The time zone value
        :return: The time zone value (if valid)
        :raise: ValueError if the time zone is invalid
        """
        if v not in pytz.common_timezones:
            msg = f"Invalid Time Zone {v}"
            logger.error(msg)
            raise ValueError(msg)
        return v


class Task(ImmutableModel):
    """
    Defines a task used to transform or update a source CSV record.
    """
    name: str = Field(description="The task name")
    comment: Optional[str]
    params: Optional[Dict[str, Any]] = Field(
        description="The task parameter name and value."
    )


class FileDefinition(ImmutableModel):
    """
    Maps a CSV file's records to FHIR resources.
    """
    comment: Optional[str]

    valueDelimiter: str = Field(
        description="The field value delimiter used in the CSV file",
        default=","
    )
    convertColumnsToString: bool = Field(
        description="Used to convert all input columns to a string representation. Defaults to True",
        default=True
    )
    resourceType: str = Field(
        description="The FHIR resource type, such as Patient or Observation"
    )
    groupByKey: str = Field(
        description="The field used to link records across CSV files"
    )

    headers: Optional[Union[List[str], List[Dict[str, str]]]] = Field(
        description="List of header columns used to parse CSV records." +
                    "Used when a source file does not include a header"
    )

    tasks: Optional[List[Task]] = Field(
        description="Tasks are used to transform CSV source records to the internal record format."
    )

    @validator("resourceType")
    def validate_resource_type(cls, v):
        """
        Validates that the resourceType is a valid FHIR resource type
        :param v: The resourceType value
        :return: The resourceType value
        :raise: ValueError if the resourceType is invalid.
        """
        if v and v.lower() not in FHIR_RESOURCES:
            msg = f"Invalid FHIR resource {v}"
            logger.error(msg)
            raise ValueError(msg)
        return v

    @root_validator
    def validate_tasks(cls, values):
        """
        Validates task definitions to ensure that they resolve to functions within the pipeline.tasks module.

        Validations include:
        - validating that the task name == a pipeline.tasks function name
        - the task params align with the pipeline.tasks function parameters

        :param values: The validated values for this DataContract instance.
        :return: The validated values if no errors are found.
        :raise: ValueError if a validation error is found
        """
        from linuxforhealth.csvtofhir.pipeline.operations import TASKS

        tasks: List[Task] = values.get("tasks", [])
        for t in tasks:
            task_function = TASKS.get(t.name)
            if task_function is None:
                msg = f"Unable to load task {t.name}"
                logger.error(msg)
                raise ValueError(msg)

            func_params: Dict[str, Parameter] = {
                fp.name: fp for fp in signature(task_function).parameters.values()
            }
            min_params: List[Parameter] = list(
                filter(is_required_parameter, func_params.values())
            )

            task_params = t.params or {}
            if len(task_params) < len(min_params):
                msg = (f"Task {t.name}: Number of provided task params {len(t.params)} < minimum required " +
                       f"{len(min_params)}")
                logger.error(msg)
                raise ValueError(msg)

            for p in task_params.keys():
                if p not in func_params:
                    msg = (f"Task {t.name}: Parameter {p} is not found in {task_function.__name__} " +
                           f"signature {list(func_params.keys())}")
                    logger.error(msg)
                    raise ValueError(msg)

        return values


class DataContract(ImmutableModel):
    """
    Specifies how CSV records are mapped to FHIR resources.
    """
    general: GeneralSection = Field(
        description="Contains settings applicable to all files"
    )
    fileDefinitions: Dict[str, FileDefinition] = Field(
        description="The DataContract's CSVToFHIR resource mappings"
    )


def load_data_contract(file_path: str) -> DataContract:
    """
    Loads a resource mapping JSON configuration from file.
    :param file_path: The path to the resource mapping configuration
    :return: dictionary
    """
    with open(file_path, "rt") as r:
        return DataContract(**json.load(r))
