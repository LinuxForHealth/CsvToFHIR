from importlib.resources import Resource
from typing import Dict, List

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.encounter import Encounter, EncounterDiagnosis
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta

from linuxforhealth.csvtofhir.fhirrs import encounter
from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ConditionResource, ExtensionUrl, SystemConstants
from linuxforhealth.csvtofhir.model.csv import csv_utils
from linuxforhealth.csvtofhir.model.csv.condition import (CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS,
                                                          CONDITION_CATEGORY_PROBLEM_LIST,
                                                          ConditionCsv)

# Map of the data to generate the SNOMED bindings for the condition-diseaseCourse extension.
# Key is the values currently supported for conditionChronicity in the pydantic model.
CHRONICITY_CONCEPTS = {
    "chronic": ["90734009", "Chronic (qualifier value)", SystemConstants.SNOMED_SYSTEM],
    "acute": ["373933003", "Acute onset", SystemConstants.SNOMED_SYSTEM]
}


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    """
    Takes an input CSV record and according to the data contract returns a FHIR resource.
    See documentation for use in implementation-guide.md
    """
    resources: list = []
    incoming_data: ConditionCsv = ConditionCsv.parse_obj(record)
    if not incoming_data.conditionCode and not incoming_data.conditionCodeText:
        return resources  # even though it is not required, we will not be creating resource without code

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    resource_id = fhir_utils.get_resource_id(incoming_data.resourceInternalId)
    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )

    condition_category = (
        [incoming_data.get_condition_category_cc()]
        if incoming_data.get_condition_category_cc()
        else None
    )

    code_cc = fhir_utils.get_codeable_concept(
        incoming_data.conditionCodeSystem,
        incoming_data.conditionCode,
        None,
        incoming_data.conditionCodeText
    )

    clinical_status = None
    if incoming_data.conditionClinicalStatus:
        clinical_status = fhir_utils.get_codeable_concept(
            SystemConstants.CONDITION_CLINICAL_STATUS_SYSTEM,
            incoming_data.conditionClinicalStatus,
            ConditionResource.clinical_status_display.get(incoming_data.conditionClinicalStatus),
            None
        )
    verification_status = None
    if incoming_data.conditionVerificationStatus:
        verification_status = fhir_utils.get_codeable_concept(
            SystemConstants.CONDITION_VERIFICATION_STATUS_SYSTEM,
            incoming_data.conditionVerificationStatus,
            ConditionResource.verification_status_display.get(incoming_data.conditionVerificationStatus),
            None
        )

    ext_id = fhir_utils.get_external_identifier(code_cc, "Condition")
    if ext_id:
        identifiers.append(ext_id)

    enc: Encounter = None
    if incoming_data.has_encounter_data():
        encounter_resources = encounter.convert_record(group_by_key, record, resource_meta)
        for r in encounter_resources:
            if r.resource_type == 'Encounter':
                enc = r
        resources.extend(encounter_resources)

    condition_extensions = []
    if incoming_data.conditionChronicity:
        chronicity = _build_chronicty_extension(incoming_data.conditionChronicity)
        condition_extensions.append(chronicity)

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.conditionSourceRecordId, resource_meta)

    fhir_resource: Condition = Condition.construct(
        id=resource_id,
        identifier=identifiers,
        category=condition_category,
        clinicalStatus=clinical_status,
        code=code_cc,
        encounter=fhir_utils.get_resource_reference(enc),
        extension=condition_extensions if len(condition_extensions) else None,
        meta=resource_meta_copy,
        recordedDate=fhir_utils.get_datetime(incoming_data.conditionRecordedDateTime, record.get('timeZone')),
        onsetDateTime=fhir_utils.get_datetime(incoming_data.conditionOnsetDateTime, record.get('timeZone')),
        abatementDateTime=fhir_utils.get_datetime(incoming_data.conditionAbatementDateTime, record.get('timeZone')),
        severity=fhir_utils.get_codeable_concept(
            incoming_data.conditionSeveritySystem,
            incoming_data.conditionSeverityCode,
            None,
            incoming_data.conditionSeverityText
        ),
        subject=patient_reference,
        verificationStatus=verification_status
    )

    _complete_encoding_setup(enc, incoming_data, code_cc, fhir_resource)

    resources.append(fhir_resource)
    return resources


def _complete_encoding_setup(
        enc: Encounter,
        incoming_data: ConditionCsv,
        code_cc: CodeableConcept,
        fhir_resource):
    if code_cc.coding:
        display_value = code_cc.coding[0].code
        if code_cc.text:
            display_value = f"{display_value} ({code_cc.text})"
    else:
        display_value = code_cc.text

    condition_reference = fhir_utils.get_resource_reference(fhir_resource, display_value)
    if enc:
        _connect_encoding_references(enc, incoming_data, condition_reference, code_cc)


def _connect_encoding_references(
        enc: Encounter,
        incoming_data: ConditionCsv,
        condition_reference,
        code_cc: CodeableConcept):
    '''
    Builds the references from Encounter to the Condition:
    - Encounter.reasonReference for Conditions with category=problem-list-item
    - Encounter.diagnosis for Conditions with category=encounter-diagnosis
    '''
    if incoming_data.conditionCategory == CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS:
        # id for the diagnosis element, uses these options in this order:
        #  1. diagnosis rank
        #  2. diagnosis.use + hyphen + Condition.code
        #  3. Condition.code
        diagnosis_id = fhir_utils.format_id_datatype(incoming_data.conditionDiagnosisRank)
        if not diagnosis_id:
            if code_cc.coding:
                diagnosis_id = code_cc.coding[0].code
            else:
                diagnosis_id = code_cc.text
        enc.diagnosis = []
        rank = incoming_data.get_encounter_diagnosis_rank_int()
        # Build Encounter.diagnosis elements, one entry per diagnosis.use
        if incoming_data.conditionRoleIsAdmitting and \
                incoming_data.conditionRoleIsAdmitting.lower() in csv_utils.TRUE_STRINGS:
            diagnosis = _build_diagnosis_with_use("AD", rank, diagnosis_id, condition_reference)
            enc.diagnosis.append(diagnosis)
        if incoming_data.conditionRoleIsChiefComplaint and \
                incoming_data.conditionRoleIsChiefComplaint.lower() in csv_utils.TRUE_STRINGS:
            diagnosis = _build_diagnosis_with_use("CC", rank, diagnosis_id, condition_reference)
            enc.diagnosis.append(diagnosis)
        if incoming_data.conditionPrincipalDiagnosis and \
                incoming_data.conditionPrincipalDiagnosis.lower() in csv_utils.TRUE_STRINGS:
            diagnosis = _build_diagnosis_with_use("principal-diagnosis", rank, diagnosis_id, condition_reference)
            enc.diagnosis.append(diagnosis)
        if not len(enc.diagnosis):  # no dianosis.use values, add single diagnosis element without 'use'
            diagnosis = EncounterDiagnosis.construct(
                id=diagnosis_id,
                rank=rank,
                condition=condition_reference
            )
            enc.diagnosis.append(diagnosis)

    elif incoming_data.conditionCategory == CONDITION_CATEGORY_PROBLEM_LIST:
        diagnosis_id = fhir_utils.format_id_datatype(condition_reference.reference)
        condition_reference.id = diagnosis_id
        enc.reasonReference = [condition_reference]


def _build_diagnosis_with_use(use_code: str, rank: int, id: str, condition_reference: str) \
        -> EncounterDiagnosis:
    use_cc = fhir_utils.get_codeable_concept(
        ExtensionUrl.ENCOUNTER_DIAGNOSIS_USE_EXTENSION_URL,
        use_code,
        fhir_constants.EncounterResource.diagnosis_use_display.get(use_code)
    )
    diagnosis = EncounterDiagnosis.construct(
        rank=rank,
        use=use_cc,
        condition=condition_reference
    )
    # Set diagnosis.id
    if rank:  # rank is first choice
        diagnosis.id = id
    else:     # role hyphen Condition.code is second choice
        diagnosis.id = use_code + "-" + id
    return diagnosis


def _build_chronicty_extension(text_value: str) -> Extension:
    chronicity = Extension.construct(url=ExtensionUrl.CHRONICITY_EXTENSION_SYSTEM)
    chronicity_cc = CodeableConcept.construct()
    chronicity_cc.text = text_value
    chronicity.valueCodeableConcept = chronicity_cc
    cc_data = CHRONICITY_CONCEPTS.get(text_value.lower())
    if cc_data:
        coding = Coding.construct()
        coding.code = cc_data[0]
        coding.display = cc_data[1]
        coding.system = cc_data[2]
        chronicity_cc.coding = [coding]
    return chronicity
