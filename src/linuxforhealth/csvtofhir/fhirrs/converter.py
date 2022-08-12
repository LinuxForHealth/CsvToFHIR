from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir import support
from linuxforhealth.csvtofhir.fhirrs import conversion_by_resource

logger = support.get_logger(__name__)


def convert_to_fhir(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[str]:
    """
    Converts a record into one or more FHIR resources.
    Results are returned as a list containing "string encoded" FHIR resources.

    :param group_by_key: A value used to group the current record with other records within a CSV batch.
    :param record: The source record.
    :return: List of converted FHIR Resources
    """
    resource_type: str = record.get("configResourceType")
    logger.debug(f"Converting FHIR resource {resource_type}.")
    conversion_func = conversion_by_resource[resource_type]
    fhir_resource_list: List[Resource] = conversion_func(
        group_by_key, record, resource_meta
    )
    if not fhir_resource_list:
        return []
    response_list: list = []
    for resource in fhir_resource_list:
        response_list.append(resource.json())
    logger.debug(f"Found {len(response_list)} resources.")
    return response_list
