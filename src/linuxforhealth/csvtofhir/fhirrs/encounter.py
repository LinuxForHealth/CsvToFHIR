from importlib.resources import Resource
from typing import Dict, List, Union

from fhir.resources.encounter import Encounter, EncounterHospitalization, \
    EncounterLocation, EncounterParticipant, EncounterStatusHistory
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.practitioner import Practitioner
from fhir.resources.patient import Patient
from fhir.resources.meta import Meta
from fhir.resources.extension import Extension

from linuxforhealth.csvtofhir.model.csv.encounter import EncounterCsv, EncounterStatusHistoryEntry
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl, SystemConstants, ValueDataAbsentReason
from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirrs import location, patient, practitioner


def get_insured_extension(incoming_data: EncounterCsv):
    # Must have a code or text to continue/
    if (
        not incoming_data.encounterInsuredCategoryCode
        and not incoming_data.encounterInsuredCategoryText
    ):
        return None  # don't create if category is not found

    # complex extension contains the two extensions above
    ext_insured: Extension = Extension.construct(
        url=ExtensionUrl.ENCOUNTER_INSURED_EXTENSION_URL,
        id=incoming_data.get_insured_entry_id()
    )

    if ext_category := fhir_utils.get_extension_with_codeable_concept(
        ExtensionUrl.ENCOUNTER_INSURED_CATEGORY_EXTENSION_URL,
        incoming_data.encounterInsuredCategoryCode,
        incoming_data.encounterInsuredCategorySystem,
        None,
        incoming_data.encounterInsuredCategoryText
    ):
        ext_insured.extension = [ext_category]

    if not ext_insured.extension:
        return None

    if ext_rank := fhir_utils.get_extension(
        ExtensionUrl.ENCOUNTER_INSURED_RANK_EXTENSION_URL,
        "valueInteger",
        incoming_data.encounterInsuredRank
    ):
        ext_insured.extension.append(ext_rank)

    return ext_insured


def get_claim_type_extension(incoming_data: EncounterCsv):
    if not incoming_data.encounterClaimType:
        return None  # don't create if claim type is not found

    ext_claim_type: Extension = Extension.construct(
        url=ExtensionUrl.ENCOUNTER_CLAIM_TYPE_EXTENSION_URL,
        valueString=incoming_data.encounterClaimType
    )
    return ext_claim_type


def get_drg_code_extension(incoming_data: EncounterCsv):
    if not incoming_data.encounterDrgCode:
        return None  # don't create if drg_code is not found

    # complex extension contains the two extensions above
    ext_drg_code: Extension = Extension.construct(
        url=SystemConstants.DRG_CODE_SYSTEM,
        valueString=incoming_data.get_drg_code()
    )
    return ext_drg_code


def get_required_field_encounter_class(incoming_data: EncounterCsv):
    if incoming_data and incoming_data.encounterClassCode:  # Encounter Class is set
        class_display = incoming_data.encounterClassText
        if not class_display:
            class_display = fhir_constants.EncounterResource.class_display.get(incoming_data.encounterClassCode, None)

        encounter_class_system = fhir_utils.get_uri_format(incoming_data.encounterClassSystem)
        return fhir_utils.get_coding(
            incoming_data.encounterClassCode,
            encounter_class_system,
            class_display
        )

    # set to temporarily unknown codeable concept
    return fhir_utils.get_coding(
        ValueDataAbsentReason.CODE_TEMPORARILY_UNKNOWN[0],
        ValueDataAbsentReason.SYSTEM,
        ValueDataAbsentReason.CODE_TEMPORARILY_UNKNOWN[1]
    )


def get_hospitalization_admit_source_cc(incoming_data: EncounterCsv):
    if not any(
        [
            incoming_data.hospitalizationAdmitSourceCode,
            incoming_data.hospitalizationAdmitSourceCodeText
        ]
    ):
        return None

    return fhir_utils.get_codeable_concept(
        incoming_data.hospitalizationAdmitSourceCodeSystem,
        incoming_data.hospitalizationAdmitSourceCode,
        fhir_constants.EncounterResource.admit_source_display.get(incoming_data.hospitalizationAdmitSourceCode, None),
        incoming_data.hospitalizationAdmitSourceCodeText
    )


def get_hospitalization_re_admission_cc(incoming_data: EncounterCsv):
    if not any(
        [
            incoming_data.hospitalizationReAdmissionCode,
            incoming_data.hospitalizationReAdmissionCodeText
        ]
    ):
        return None

    return fhir_utils.get_codeable_concept(
        incoming_data.hospitalizationReAdmissionCodeSystem,
        "R" if incoming_data.hospitalizationReAdmissionCode else None,
        "Re-admission" if incoming_data.hospitalizationReAdmissionCode else None,
        incoming_data.hospitalizationReAdmissionCodeText
    )


def get_hospitalization_discharge_disposition_cc(incoming_data: EncounterCsv):
    if not any(
        [
            incoming_data.hospitalizationDischargeDispositionCode,
            incoming_data.hospitalizationDischargeDispositionCodeText
        ]
    ):
        return None

    return fhir_utils.get_codeable_concept(
        incoming_data.hospitalizationDischargeDispositionCodeSystem,
        incoming_data.hospitalizationDischargeDispositionCode,
        None,
        incoming_data.hospitalizationDischargeDispositionCodeText
    )


def get_hospitalization_object(incoming_data: EncounterCsv) -> EncounterHospitalization:
    if not incoming_data.contains_hospitalization_entries():
        return None
    hosp: EncounterHospitalization = EncounterHospitalization.construct()
    hosp.admitSource = get_hospitalization_admit_source_cc(incoming_data)
    hosp.reAdmission = get_hospitalization_re_admission_cc(incoming_data)
    hosp.dischargeDisposition = get_hospitalization_discharge_disposition_cc(incoming_data)
    return hosp


def get_reason_cc_list(incoming_data):
    cc = fhir_utils.get_codeable_concept(
        incoming_data.encounterReasonCodeSystem,
        incoming_data.encounterReasonCode,
        None,
        incoming_data.encounterReasonCodeText
    )
    return [cc] if cc else None


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []
    """
    Takes an input CSV record and according to the data contract returns a FHIR resource.
    See documentation for use in implementation-guide.md
    """
    if record.get("encounterInternalId"):
        # coming from other
        record["resourceInternalId"] = record.get("encounterInternalId")
    incoming_data: EncounterCsv = EncounterCsv.parse_obj(record)

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    resource_id = fhir_utils.format_id_datatype(
        getattr(incoming_data, "resourceInternalId", None))  # default to None if resourceInternalId not there
    patient_internal_id = fhir_utils.get_resource_id(
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.encounterSourceRecordId, resource_meta)

    fhir_resource: Encounter = Encounter.construct(
        id=fhir_utils.get_resource_id(resource_id),
        identifier=identifiers,
        status=incoming_data.encounterStatus,
        subject=fhir_utils.get_resource_reference_from_str("Patient", patient_internal_id),
        class_fhir=get_required_field_encounter_class(incoming_data),
        meta=resource_meta_copy
    )
    fhir_resource.period = fhir_utils.get_fhir_type_period(
        incoming_data.encounterStartDateTime, incoming_data.encounterEndDateTime, record.get('timeZone'))
    fhir_resource.hospitalization = get_hospitalization_object(incoming_data)
    fhir_resource.priority = fhir_utils.get_codeable_concept(
        incoming_data.encounterPriorityCodeSystem,
        incoming_data.encounterPriorityCode,
        None,
        incoming_data.encounterPriorityText
    )

    # fhir_resource.statusHistory
    encounter_status_history_list = []
    if incoming_data.encounterStatusHistory:
        for status_history_string in incoming_data.encounterStatusHistory:
            status_history_string_split_array = status_history_string.split("^")
            # get the list of fields from the EncounterStatusHistoryEntry class
            model_fields = list(EncounterStatusHistoryEntry.__fields__)
            values = {}
            # pull the values in the order they appear in the EncounterStatusHistoryEntry class
            for i in range(len(model_fields)):
                values[model_fields[i]] = status_history_string_split_array[i]
            status = values['status'] if values['status'] else None
            start_time = values['start_time'] if values['start_time'] and values['start_time'] != 'None' else None
            end_time = values['end_time'] if values['end_time'] and values['end_time'] != 'None' else None
            # create the EncounterStatusHistory
            if start_time or end_time:
                encounter_status_history = EncounterStatusHistory.construct(
                    status=status,
                    period=fhir_utils.get_fhir_type_period(start_time, end_time, record.get('timeZone'))
                )
                encounter_status_history_list.append(encounter_status_history)

    if len(encounter_status_history_list):
        fhir_resource.statusHistory = encounter_status_history_list

    # patient
    patient_resources = patient.convert_record(group_by_key, record, resource_meta)
    resources.extend(patient_resources)

    # practitioner
    practitioner_resources: list = practitioner.convert_record(group_by_key, record, resource_meta)
    _add_practioner(fhir_resource, incoming_data, resources, practitioner_resources)

    # if the practitioner is primary care then create a patient with the generalPracitioner set to the practitioner role
    # encounterParticipantTypeText means a Role object would have been created
    if "encounterParticipantTypeText" in record and record["encounterParticipantTypeText"] == "PRIMARY_CARE":
        patient_id = (
            fhir_utils.format_id_datatype(incoming_data.patientInternalId)
            if incoming_data.patientInternalId
            else fhir_utils.format_id_datatype(group_by_key)
        )
        # For the patient's identifier use the patientInternalId if it's there otherwise use accountNumber
        if incoming_data.dict()["patientInternalId"]:
            # PI
            patient_identifiers = fhir_identifier_utils.create_identifier_list(
                {"patientInternalId": incoming_data.patientInternalId})
        else:
            # AN
            patient_identifiers = fhir_identifier_utils.create_identifier_list(
                {"accountNumber": incoming_data.accountNumber})

        patient_resource = Patient.construct(
            id=patient_id,
            identifier=patient_identifiers,
            meta=resource_meta,
            generalPractitioner=[
                fhir_utils.get_resource_reference_from_str("PractitionerRole", incoming_data.practitionerInternalId)
            ]
        )
        resources.append(patient_resource)

    # location
    location_resources = location.convert_record(group_by_key, record, resource_meta)
    _add_location(fhir_resource, incoming_data, resources, location_resources)

    fhir_resource.length = fhir_utils.get_duration(
        incoming_data.encounterLengthValue,
        incoming_data.encounterLengthUnits)
    fhir_resource.reasonCode = get_reason_cc_list(incoming_data)

    # extensions
    _add_extensions(fhir_resource, incoming_data)

    resources.append(fhir_resource)
    return resources


def _add_practioner(
        fhir_resource: Encounter,
        incoming_data: EncounterCsv,
        resources: list,
        practitioner_resources: list):
    """
    Adds practitioner references if present to the fhir_resource.
    """
    if practitioner_resources:
        resources.extend(practitioner_resources)
        pr: Union[Practitioner, PractitionerRole] = practitioner_resources[0]
        ep_id = incoming_data.encounterParticipantSequenceId
        if not ep_id:
            if incoming_data.practitionerNPI:
                ep_id = fhir_identifier_utils.IdentifierType.NPI_NUMBER[0] + "." + incoming_data.practitionerNPI
            elif incoming_data.practitionerInternalId:
                ep_id = fhir_identifier_utils.IdentifierType.RESOURCE_IDENTIFIER[0] + \
                    "." + incoming_data.practitionerInternalId
            if incoming_data.encounterParticipantTypeCode:
                ep_id = f'{incoming_data.encounterParticipantTypeCode}.{ep_id}'
            elif incoming_data.encounterParticipantTypeText:
                ep_id = f'{incoming_data.encounterParticipantTypeText}.{ep_id}'

        ep: EncounterParticipant = EncounterParticipant.construct(
            individual=fhir_utils.get_resource_reference(pr),
            id=fhir_utils.format_id_datatype(ep_id)
        )
        the_type = fhir_utils.get_codeable_concept(
            incoming_data.encounterParticipantTypeCodeSystem,
            incoming_data.encounterParticipantTypeCode,
            fhir_constants.EncounterResource.participant_type_display.get(
                incoming_data.encounterParticipantTypeCode, None),
            incoming_data.encounterParticipantTypeText)
        ep.type = [the_type] if the_type else None
        fhir_resource.participant = [ep]


def _add_location(fhir_resource: Encounter, incoming_data: EncounterCsv, resources: list, location_resources: list):
    """
    Adds location references if present to the fhir_resource.
    """
    resources.extend(location_resources)
    if len(location_resources) == 1:
        encounter_location: EncounterLocation = EncounterLocation.construct(
            id=fhir_utils.format_id_datatype(incoming_data.encounterLocationSequenceId),
            location=fhir_utils.get_resource_reference(location_resources[0])
        )
        encounter_location.period = fhir_utils.get_fhir_type_period(
            incoming_data.encounterLocationPeriodStart,
            incoming_data.encounterLocationPeriodEnd
        )
        fhir_resource.location = [encounter_location]
    elif len(location_resources) > 1:
        fhir_resource.location = []
        for location_resource in location_resources:
            encounter_location: EncounterLocation = EncounterLocation.construct(
                location=fhir_utils.get_resource_reference(location_resource)
            )
            fhir_resource.location.append(encounter_location)


def _add_extensions(fhir_resource: Encounter, incoming_data: EncounterCsv):
    """
    Adds extensions if needed to the fhir_resource.
    """
    insured_ext = get_insured_extension(incoming_data)
    claim_ext = get_claim_type_extension(incoming_data)
    drg_code_ext = get_drg_code_extension(incoming_data)
    # only create the extension list if there is at least one extension
    if insured_ext or drg_code_ext or claim_ext:
        fhir_resource.extension = []
        # add each extension that exists
        if insured_ext:
            fhir_resource.extension.append(insured_ext)
        if drg_code_ext:
            fhir_resource.extension.append(drg_code_ext)
        if claim_ext:
            fhir_resource.extension.append(claim_ext)
