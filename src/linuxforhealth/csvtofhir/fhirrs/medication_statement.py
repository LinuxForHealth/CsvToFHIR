from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import medication_use
from linuxforhealth.csvtofhir.model.csv.medication_use import RESOURCE_TYPE_MED_STATEMENT


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    record["resourceType"] = RESOURCE_TYPE_MED_STATEMENT
    return medication_use.convert_record(group_by_key, record, resource_meta)
