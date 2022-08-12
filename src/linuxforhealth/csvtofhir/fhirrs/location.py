from typing import Dict, List

from fhir.resources.location import Location
from fhir.resources.meta import Meta

from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.model.csv.location import LocationCsv


def get_location_type_cc_list(record: LocationCsv):
    cc = fhir_utils.get_codeable_concept(
        record.locationTypeCodeSystem,
        record.locationTypeCode,
        fhir_constants.LocationResource.type_display.get(record.locationTypeCode, None),
        record.locationTypeText
    )
    return [cc] if cc else None


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Location]:
    csv_record: LocationCsv = LocationCsv.parse_obj(record)
    if not csv_record.contains_location_data():
        return []

    resources = []
    identifiers = fhir_identifier_utils.create_identifier_list(csv_record.dict())

    rs_location: Location = Location.construct(
        id=fhir_utils.get_resource_id(csv_record.resourceInternalId),
        identifier=identifiers,
        meta=resource_meta,
        name=csv_record.locationName,
        type=get_location_type_cc_list(csv_record)
    )

    resources.append(rs_location)
    return resources
