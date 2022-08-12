from importlib.resources import Resource
from typing import Dict, List

from fhir.resources.allergyintolerance import AllergyIntolerance, AllergyIntoleranceReaction
from fhir.resources.meta import Meta

from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.allergy_intolerance import (DEFAULT_ALLERGY_CLINICAL_STATUS_CODE,
                                                                    AllergyIntoleranceCsv)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []

    incoming_data: AllergyIntoleranceCsv = AllergyIntoleranceCsv.parse_obj(record)
    if not incoming_data.allergyCode and not incoming_data.allergyCodeText:
        return resources  # even though it is not required, we will not be creating resource without code

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    resource_id = fhir_utils.get_resource_id(incoming_data.resourceInternalId)
    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )

    clinical_status_cc = None
    if incoming_data.allergyClinicalStatusCode is not None:
        allergy_clinical_status_display = fhir_constants.AllergyIntoleranceResource.allergy_clinical_status_display.get(
            incoming_data.allergyClinicalStatusCode, None)

        clinical_status_cc = fhir_utils.get_codeable_concept(
            SystemConstants.ALLERGY_CLINICAL_STATUS_SYSTEM,
            incoming_data.allergyClinicalStatusCode,
            allergy_clinical_status_display,
            None
        )

    code_cc = fhir_utils.get_codeable_concept(
        incoming_data.allergyCodeSystem,
        incoming_data.allergyCode,
        None,
        incoming_data.allergyCodeText
    )
    ext_id = fhir_utils.get_external_identifier(code_cc, "AllergyIntolerance")
    if ext_id:
        identifiers.append(ext_id)

    verification_status_cc = None
    if incoming_data.allergyVerificationStatusCode is not None:
        allergy_verification_status_display = fhir_constants.AllergyIntoleranceResource.allergy_verification_status_display.get(
            incoming_data.allergyVerificationStatusCode, None)

        verification_status_cc = fhir_utils.get_codeable_concept(
            SystemConstants.ALLERGY_VERIFICATION_STATUS_SYSTEM,
            incoming_data.allergyVerificationStatusCode,
            allergy_verification_status_display,
            None
        )

    # FHIR validation for AllergyIntolerance resource requires either:
    #  verificationStatus = Entered in error. OR
    #  verificationStatus != Entered in error AND clinicalStatus. OR
    #  clinicalStatus AND no verificationStatus.
    # If a clinicalStatus is not provided and one is required to satisfy the rules, a default is provided.
    if clinical_status_cc is None and (
            incoming_data.allergyVerificationStatusCode is None or
            incoming_data.allergyVerificationStatusCode != "entered-in-error"):
        clinical_status_cc = fhir_utils.get_codeable_concept(
            SystemConstants.ALLERGY_CLINICAL_STATUS_SYSTEM,
            DEFAULT_ALLERGY_CLINICAL_STATUS_CODE,
            # Display value is based on lookup of DEFAULT_ALLERGY_CLINICAL_STATUS_CODE.
            fhir_constants.AllergyIntoleranceResource.allergy_clinical_status_display.get(
                DEFAULT_ALLERGY_CLINICAL_STATUS_CODE, None),
            None
        )

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.allergySourceRecordId, resource_meta)

    fhir_resource: AllergyIntolerance = AllergyIntolerance.construct(
        id=resource_id,
        identifier=identifiers,
        type=incoming_data.allergyType,
        criticality=incoming_data.allergyCriticality,
        category=[incoming_data.allergyCategory]
        if incoming_data.allergyCategory
        else None,
        patient=patient_reference,
        encounter=fhir_utils.get_resource_reference_from_str("Encounter", incoming_data.encounterInternalId),
        code=code_cc,
        recordedDate=fhir_utils.get_datetime(incoming_data.allergyRecordedDateTime),
        meta=resource_meta_copy,
        clinicalStatus=clinical_status_cc,
        verificationStatus=verification_status_cc
    )

    fhir_resource.onsetPeriod = fhir_utils.get_fhir_type_period(
        incoming_data.allergyOnsetStartDateTime,
        incoming_data.allergyOnsetEndDateTime,
        record.get('timeZone'))

    reaction: AllergyIntoleranceReaction = None
    if incoming_data.has_reaction_data():
        reaction = AllergyIntoleranceReaction.construct(
            manifestation=incoming_data.get_allergy_manifestation_cc_list()
        )
    if reaction:
        fhir_resource.reaction = [reaction]

    resources.append(fhir_resource)
    return resources
