from typing import Dict, List, Union

from fhir.resources.encounter import Encounter
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta
from fhir.resources.procedure import Procedure, ProcedurePerformer
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import encounter, practitioner
from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl
from linuxforhealth.csvtofhir.model.csv.procedure import ProcedureCsv


def get_modifier_extensions(incoming_data: ProcedureCsv) -> Union[List[Extension], None]:
    modifiers = incoming_data.get_modifier_list()
    if not modifiers:
        return None
    extensions_list: List[Extension] = []
    for m in modifiers:
        ext: Extension = Extension.construct(url=ExtensionUrl.PROCEDURE_MODIFIER_EXTENSION_URL)
        ext.valueCodeableConcept = fhir_utils.get_codeable_concept(
            incoming_data.procedureModifierSystem, m, None
        )
        extensions_list.append(ext)
    return extensions_list if extensions_list else None


def get_procedure_sequence_extensions(incoming_data: ProcedureCsv) -> Union[List[Extension], None]:
    if not incoming_data.procedureEncounterSequenceId:
        return None
    extensions_list: List[Extension] = []
    ext: Extension = Extension.construct(url=ExtensionUrl.PROCEDURE_SEQUENCE_EXTENSION_URL)
    ext.valueString = incoming_data.procedureEncounterSequenceId
    extensions_list.append(ext)
    return extensions_list if extensions_list else None


def convert_record(group_by_key: str, record: Dict, resource_meta: Meta = None) -> List[Resource]:
    resources: list = []

    incoming_data: ProcedureCsv = ProcedureCsv.parse_obj(record)
    if not incoming_data.procedureCode and not incoming_data.procedureCodeText and len(
            incoming_data.procedureCodeList) == 0:
        return resources  # even though it is not required, we will not be creating procedure without code

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    resource_id = fhir_utils.get_resource_id(incoming_data.resourceInternalId)
    # only creating patient reference, assume it's created elsewhere
    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        incoming_data.patientInternalId
        if incoming_data.patientInternalId
        else group_by_key
    )
    code_cc = fhir_utils.get_codeable_concept(
        incoming_data.procedureCodeSystem,
        incoming_data.procedureCode,
        incoming_data.procedureCodeDisplay,
        incoming_data.procedureCodeText
    )
    # handle additional codes in procedureCodeList
    code_cc = fhir_utils.add_hl7_style_coded_list_to_codeable_concept(
        incoming_data.procedureCodeList, code_cc, incoming_data.assigningAuthority)
    # If all the procedureCodes are incomplete, no code_cc is created
    # If so, don't create procedure.  Simply return.
    if code_cc is None:
        return resources

    # Add extId, using codes
    ext_id = fhir_utils.get_external_identifier(code_cc, "Procedure")
    if ext_id:
        identifiers.append(ext_id)

    enc: Encounter = None
    performer = None
    if incoming_data.has_encounter_data():
        encounter_resources = encounter.convert_record(
            group_by_key, record, resource_meta
        )
        r: Resource
        for r in encounter_resources:
            if r.resource_type == "Encounter":
                enc = r
            if r.resource_type == "Practitioner" and not performer:
                performer = r
            if r.resource_type == "PractitionerRole":
                performer = r  # preferred
        resources.extend(encounter_resources)
    else:  # try to extract performer on our own
        practitioner_resources = practitioner.convert_record(
            group_by_key, record, resource_meta
        )
        if practitioner_resources:
            performer = practitioner_resources[0]
            resources.extend(practitioner_resources)

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.procedureSourceRecordId, resource_meta)

    fhir_resource: Procedure = Procedure.construct(
        id=resource_id,
        identifier=identifiers,
        status=incoming_data.procedureStatus,
        category=fhir_utils.get_codeable_concept(
            incoming_data.procedureCategorySystem,
            incoming_data.procedureCategory,
            None,
            incoming_data.procedureCategoryText
        ),
        subject=patient_reference,
        encounter=fhir_utils.get_resource_reference(enc),
        code=code_cc,
        performedDateTime=fhir_utils.get_datetime(
            incoming_data.procedurePerformedDateTime, record.get('timeZone')
        ),
        extension=get_modifier_extensions(incoming_data),
        meta=resource_meta_copy
    )
    if performer:
        fhir_resource.performer = [
            ProcedurePerformer.construct(
                actor=fhir_utils.get_resource_reference(performer)
            )
        ]

    if enc:
        list_id = fhir_resource.id
        proc_reference = fhir_utils.get_resource_reference(fhir_resource, None, list_id)
        procedure_seq_ext = get_procedure_sequence_extensions(incoming_data)
        proc_reference.extension = procedure_seq_ext
        enc.reasonReference = [proc_reference] if proc_reference else None
    resources.append(fhir_resource)
    return resources
