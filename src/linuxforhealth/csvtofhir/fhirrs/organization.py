from importlib.resources import Resource
from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.organization import Organization

from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.model.csv.organization import OrganizationCsv
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources = []
    csv_record: OrganizationCsv = OrganizationCsv.parse_obj(record)

    identifiers = fhir_identifier_utils.create_identifier_list(csv_record.dict())
    organization_id = fhir_utils.get_resource_id(csv_record.resourceInternalId)

    organization_resource: Organization = Organization.construct(
        id=organization_id,
        identifier=identifiers,
        meta=resource_meta,
        name=csv_record.organizationName
    )
    resources.append(organization_resource)
    return resources
