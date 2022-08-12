from typing import Dict, List

from fhir.resources.immunization import Immunization
from fhir.resources.meta import Meta
from fhir.resources.organization import Organization
from fhir.resources.quantity import Quantity
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import organization
from linuxforhealth.csvtofhir.fhirutils import csv_utils, fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.model.csv.immunization import ImmunizationCsv


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []
    incoming_data: ImmunizationCsv = ImmunizationCsv.parse_obj(record)

    # Cannot create valid resource without code
    if not incoming_data.immunizationVaccineCode:
        return resources  # Empty list

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    vaccine_cc = fhir_utils.get_codeable_concept(
        incoming_data.immunizationVaccineSystem,
        incoming_data.immunizationVaccineCode,
        incoming_data.immunizationVaccineDisplay,
        incoming_data.immunizationVaccineText
    )
    # handle additional codes in immunizationCodeList
    vaccine_cc = fhir_utils.add_hl7_style_coded_list_to_codeable_concept(
        incoming_data.immunizationVaccineCodeList, vaccine_cc, incoming_data.assigningAuthority)

    # Add extId, using codes
    ext_id = fhir_utils.get_external_identifier(vaccine_cc, "Immunization")
    if ext_id:
        identifiers.append(ext_id)

    route_cc = None
    if incoming_data.immunizationRouteCode:
        route_cc = fhir_utils.get_codeable_concept(
            incoming_data.immunizationRouteSystem,
            incoming_data.immunizationRouteCode,
            None,
            incoming_data.immunizationRouteText
        )

    site_cc = None
    if incoming_data.immunizationSiteCode:
        site_cc = fhir_utils.get_codeable_concept(
            incoming_data.immunizationSiteSystem,
            incoming_data.immunizationSiteCode,
            None,
            incoming_data.immunizationSiteText
        )

    status_reason_cc = None
    if incoming_data.immunizationStatusReasonCode:
        status_reason_cc = fhir_utils.get_codeable_concept(
            incoming_data.immunizationStatusReasonSystem,
            incoming_data.immunizationStatusReasonCode,
            fhir_constants.ImmunizationResource.immunization_status_reason_display.get(
                incoming_data.immunizationStatusReasonCode, None),
            incoming_data.immunizationStatusReasonText
        )

    resource_id = fhir_utils.format_id_datatype(incoming_data.resourceInternalId)
    # Create a patient reference
    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )

    organization_resources: Organization = None
    organization_reference = None
    if incoming_data.organizationName:
        organization_resources = organization.convert_record(group_by_key, record, resource_meta)
        resources.extend(organization_resources)

        organization_reference = fhir_utils.get_resource_reference_from_str(
            "Organization",
            organization_resources[0].id
            if organization_resources[0].id
            else group_by_key,
            incoming_data.organizationName  # display
        )

    dosage_qty: Quantity = None
    if incoming_data.immunizationDoseQuantity and fhir_utils.is_valid_decimal(incoming_data.immunizationDoseQuantity):
        dosage_qty = Quantity.construct(
            value=float(incoming_data.immunizationDoseQuantity),
            unit=incoming_data.immunizationDoseUnit
        )

    # depending on data create a date or unknown
    occurrence_datetime = None
    occurrence_string = None
    if incoming_data.immunizationDate:
        time_zone = record.get('timeZone')
        occurrence_datetime = fhir_utils.get_datetime(incoming_data.immunizationDate, time_zone)
    else:
        occurrence_string = 'unknown'

    # Use copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.immunizationSourceRecordId, resource_meta)

    fhir_resource: Immunization = Immunization.construct(
        id=fhir_utils.get_resource_id(resource_id),
        identifier=identifiers,
        status=incoming_data.immunizationStatus,
        vaccineCode=vaccine_cc,
        occurrenceDateTime=occurrence_datetime,  # only one has value
        occurrenceString=occurrence_string,  # only one has value
        expirationDate=csv_utils.format_date(incoming_data.immunizationExpirationDate),
        encounter=fhir_utils.get_resource_reference_from_str("Encounter", incoming_data.encounterInternalId),
        doseQuantity=dosage_qty,
        patient=patient_reference,
        route=route_cc,
        site=site_cc,
        statusReason=status_reason_cc,
        manufacturer=organization_reference,
        meta=resource_meta_copy,
    )

    resources.append(fhir_resource)
    return resources
