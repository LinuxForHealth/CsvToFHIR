from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import medication_use
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.model.csv.medication_use import (RESOURCE_TYPE_MED_ADMINISTRATION,
                                                               RESOURCE_TYPE_MED_STATEMENT,
                                                               MEDICATION_STATEMENT_DEFAULT_STATUS)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    if fhir_utils.get_datetime(record.get("medicationUseOccuranceDateTime")):
        # required field for administration, time when medication was administered
        record["resourceType"] = RESOURCE_TYPE_MED_ADMINISTRATION
    else:
        record["resourceType"] = RESOURCE_TYPE_MED_STATEMENT
        record["medicationUseStatus"] = MEDICATION_STATEMENT_DEFAULT_STATUS
    return medication_use.convert_record(group_by_key, record, resource_meta)
