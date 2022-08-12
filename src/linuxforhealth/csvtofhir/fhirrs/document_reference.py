from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import unstructured
from linuxforhealth.csvtofhir.model.csv.unstructured import RESOURCE_TYPE_DOC_REFERENCE


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    # Valid entries is None or DiagnosticReport
    record["resourceType"] = RESOURCE_TYPE_DOC_REFERENCE
    return unstructured.convert_record(group_by_key, record, resource_meta)
