from typing import Dict, List, Union

from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.medicationadministration import (
    MedicationAdministration, MedicationAdministrationDosage)
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.meta import Meta
from fhir.resources.quantity import Quantity
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import medication_request
from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl
from linuxforhealth.csvtofhir.model.csv import medication_use
from linuxforhealth.csvtofhir.model.csv.medication_use import (
    MEDICATION_ADMINISTRATION_DEFAULT_STATUS,
    MEDICATION_REQUEST_DEFAULT_STATUS, MEDICATION_STATEMENT_DEFAULT_STATUS,
    RESOURCE_TYPE_MED_ADMINISTRATION, RESOURCE_TYPE_MED_REQUEST,
    MedicationUseCsv)
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def add_dosage_data(
    fhir_resource: Union[MedicationAdministration, MedicationStatement, MedicationRequest],
    incoming_data: MedicationUseCsv
):
    if not incoming_data.contains_dosage_entries():
        return

    route_cc = fhir_utils.get_codeable_concept(
        incoming_data.medicationUseRouteCodeSystem,
        incoming_data.medicationUseRouteCode,
        None,
        incoming_data.medicationUseRouteText,
    )

    route_cc = fhir_utils.add_hl7_style_coded_list_to_codeable_concept(
        incoming_data.medicationUseRouteList, route_cc, incoming_data.assigningAuthority)

    dosage_qty: Quantity = None
    if incoming_data.medicationUseDosageValue:
        try:
            value_num = float(incoming_data.medicationUseDosageValue)
        except ValueError:
            logger.warning("medicationUseDosageValue not a number")
        dosage_qty = Quantity.construct(
            value=value_num,
            unit=incoming_data.medicationUseDosageUnit
        )

    if incoming_data.resourceType == medication_use.RESOURCE_TYPE_MED_ADMINISTRATION:
        dosage_obj: MedicationAdministrationDosage = (
            MedicationAdministrationDosage.construct(
                text=incoming_data.medicationUseDosageText,
                route=route_cc,
                dose=dosage_qty
            )
        )

        if dosage_obj.dose is None:
            ext = fhir_utils.get_extension(ExtensionUrl.DATA_ABSENT_EXTENSION_URL, "valueCode", "as-text")
            dosage_obj.dose = Quantity.construct()
            dosage_obj.dose.extension = [ext]

        fhir_resource.dosage = dosage_obj
        return

    dosage_obj: Dosage = Dosage.construct(
        text=incoming_data.medicationUseDosageText,
        route=route_cc
    )
    if dosage_qty:
        dr: DosageDoseAndRate = DosageDoseAndRate.construct(doseQuantity=dosage_qty)
        dosage_obj.doseAndRate = [dr]

    if not dosage_obj:
        return

    if incoming_data.resourceType == medication_use.RESOURCE_TYPE_MED_STATEMENT:
        fhir_resource.dosage = [dosage_obj]
    elif incoming_data.resourceType == medication_use.RESOURCE_TYPE_MED_REQUEST:
        fhir_resource.dosageInstruction = [dosage_obj]


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []
    incoming_data: MedicationUseCsv = MedicationUseCsv.parse_obj(record)

    # Cannot create resource without required data
    if not incoming_data.medicationCode and not incoming_data.medicationCodeText \
       and not incoming_data.medicationCodeList:
        return resources  # Empty list

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    # do not want to set text to the first code.display if it is None
    medication_cc = fhir_utils.get_codeable_concept_no_text_default(
        incoming_data.medicationCodeSystem,
        incoming_data.medicationCode,
        incoming_data.medicationCodeDisplay,
        incoming_data.medicationCodeText
    )
    medication_cc = fhir_utils.add_hl7_style_coded_list_to_codeable_concept(
        incoming_data.medicationCodeList, medication_cc, incoming_data.assigningAuthority)

    # Add extId, using codes
    ext_id = fhir_utils.get_external_identifier(medication_cc, incoming_data.resourceType)
    if ext_id:
        identifiers.append(ext_id)

    resource_id = fhir_utils.format_id_datatype(incoming_data.resourceInternalId)
    # only creating patient reference, assume it's created elsewhere
    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )
    encounter_reference = fhir_utils.get_resource_reference_from_str(
        "Encounter", incoming_data.encounterInternalId
    )

    if incoming_data.medicationUseStatus:
        med_status = incoming_data.medicationUseStatus
    else:
        if incoming_data.resourceType == RESOURCE_TYPE_MED_ADMINISTRATION:
            med_status = MEDICATION_ADMINISTRATION_DEFAULT_STATUS
        elif incoming_data.resourceType == RESOURCE_TYPE_MED_REQUEST:
            med_status = MEDICATION_REQUEST_DEFAULT_STATUS
        else:
            med_status = MEDICATION_STATEMENT_DEFAULT_STATUS

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.medicationSourceRecordId, resource_meta)

    if incoming_data.resourceType == RESOURCE_TYPE_MED_ADMINISTRATION:
        fhir_resource: MedicationAdministration = MedicationAdministration.construct(
            context=encounter_reference,
            effectiveDateTime=fhir_utils.get_datetime(incoming_data.medicationUseOccuranceDateTime),
            id=fhir_utils.get_resource_id(resource_id),
            identifier=identifiers,
            medicationCodeableConcept=medication_cc,
            meta=resource_meta_copy,
            status=med_status,
            subject=patient_reference
        )
    elif incoming_data.resourceType == RESOURCE_TYPE_MED_REQUEST:
        fhir_resource: MedicationRequest = MedicationRequest.construct(
            authoredOn=fhir_utils.get_datetime(incoming_data.medicationAuthoredOn, record.get('timeZone')),
            encounter=encounter_reference,
            id=fhir_utils.get_resource_id(resource_id),
            identifier=identifiers,
            intent=incoming_data.medicationRequestIntent,
            medicationCodeableConcept=medication_cc,
            meta=resource_meta_copy,
            subject=patient_reference,
            status=med_status
        )
        medication_request.construct_dispense(incoming_data, fhir_resource, record)
        enc = medication_request.create_encounter(incoming_data, group_by_key, record, resource_meta)
        if enc is not None:
            resources.append(enc)

    else:
        fhir_resource: MedicationStatement = MedicationStatement.construct(
            context=encounter_reference,
            effectiveDateTime=fhir_utils.get_datetime(incoming_data.medicationUseOccuranceDateTime),
            id=fhir_utils.get_resource_id(resource_id),
            identifier=identifiers,
            status=med_status,
            medicationCodeableConcept=medication_cc,
            meta=resource_meta_copy,
            subject=patient_reference
        )

    fhir_resource.category = fhir_utils.get_codeable_concept(
        incoming_data.get_default_category_system(),
        incoming_data.medicationUseCategoryCode,
        None,
        incoming_data.medicationUseCategoryCodeText
    )

    add_dosage_data(fhir_resource, incoming_data)
    resources.append(fhir_resource)
    return resources
