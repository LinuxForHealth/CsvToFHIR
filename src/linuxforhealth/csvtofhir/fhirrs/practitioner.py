from typing import Dict, List, Union

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.humanname import HumanName
from fhir.resources.meta import Meta
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole

from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.model.csv import practitioner
from linuxforhealth.csvtofhir.model.csv.practitioner import PractitionerCsv
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def get_practitioner_role_list_cc(record: PractitionerCsv):
    fields = [
        record.practitionerRoleText,
        record.practitionerRoleCode,
        record.practitionerRoleCodeList,
    ]
    if not any(fields):
        return None
    # TODO: not implemented
    if record.practitionerRoleCodeList:
        logger.warning("Practitioner Role Code List conversion is not implemented")
        return None

    cc = fhir_utils.get_codeable_concept(
        record.practitionerRoleCodeSystem,
        record.practitionerRoleCode,
        None,
        record.practitionerRoleText
    )
    cc.id = fhir_utils.format_id_datatype(
        record.practitionerRoleCode
        if record.practitionerRoleCode
        else record.practitionerRoleText
    )
    return [cc] if cc else None


def get_practitioner_specialty_list_cc(record: PractitionerCsv) -> Union[List[CodeableConcept], None]:
    fields = [
        record.practitionerSpecialtyText,
        record.practitionerSpecialtyCode,
        record.practitionerSpecialtyCodeList
    ]
    if not any(fields):
        return None

    # We should only get the List OR Code and Text.
    cc_list = []

    # We have the speciality list
    if record.practitionerSpecialtyCodeList:
        for speciality in record.practitionerSpecialtyCodeList:
            if not speciality:
                continue

            # create the codeable concept
            cc = fhir_utils.add_hl7_style_codeable_concept(speciality)

            # determine the id
            codeable_concept_item_list = speciality.split("^")
            # use the code if it's there
            if codeable_concept_item_list[0]:
                speciality_id = codeable_concept_item_list[0]
            # otherwise use the display
            elif len(codeable_concept_item_list) > 1 and codeable_concept_item_list[1]:
                speciality_id = codeable_concept_item_list[1]
            # otherwise use the text
            elif len(codeable_concept_item_list) > 3 and codeable_concept_item_list[3]:
                speciality_id = codeable_concept_item_list[3]
            # add the id
            cc.id = fhir_utils.format_id_datatype(speciality_id)

            cc_list.append(cc)
        return cc_list

    # Otherwise we just have speciality code and/or text.
    else:
        cc = fhir_utils.get_codeable_concept(
            practitioner.PRACTITIONER_TAXONOMY_DEFAULT_SYSTEM,
            record.practitionerSpecialtyCode,
            None,
            record.practitionerSpecialtyText
        )
        cc.id = fhir_utils.format_id_datatype(
            record.practitionerSpecialtyCode[:64]  # only take the first 64 chars because 64 is the FHIR id size limit
            if record.practitionerSpecialtyCode
            else record.practitionerSpecialtyText
        )

        return [cc] if cc else None


def get_practitioner_human_name_list(record: PractitionerCsv):
    fields = [record.practitionerNameFirst, record.practitionerNameLast, record.practitionerNameText]
    if not any(fields):
        return None

    if record.practitionerNameLast:
        name = fhir_utils.get_fhir_human_name(record.practitionerNameLast, record.practitionerNameFirst)
    else:
        name = HumanName.construct(text=record.practitionerNameText)

    return [name] if name else None


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Union[PractitionerRole, Practitioner]]:
    resources = []
    csv_record: PractitionerCsv = PractitionerCsv.parse_obj(record)

    if (
        not csv_record.contains_practitioner_data()
        and not csv_record.contains_practitioner_role_data()
    ):
        return resources

    identifiers = fhir_identifier_utils.create_identifier_list(csv_record.dict())

    practitioner_id = (
        fhir_utils.get_resource_id(csv_record.resourceInternalId)
        if csv_record.resourceInternalId
        else fhir_utils.get_resource_id(csv_record.identifier_practitionerNPI)
    )

    practitioner_resource: Practitioner = None
    practitioner_role_resource: PractitionerRole = None
    if csv_record.contains_practitioner_data():
        practitioner_resource = Practitioner.construct(
            id=practitioner_id,
            identifier=identifiers,
            meta=resource_meta
        )
        practitioner_resource.name = get_practitioner_human_name_list(csv_record)
        practitioner_resource.gender = csv_record.practitionerGender

    if csv_record.contains_practitioner_role_data():
        practitioner_role_resource = PractitionerRole.construct(
            id=practitioner_id,
            identifier=identifiers,
            meta=resource_meta,
            practitioner=fhir_utils.get_resource_reference(practitioner_resource)
        )
        practitioner_role_resource.code = get_practitioner_role_list_cc(csv_record)
        practitioner_role_resource.specialty = get_practitioner_specialty_list_cc(csv_record)

    if practitioner_role_resource:
        resources.append(practitioner_role_resource)
    if practitioner_resource:
        resources.append(practitioner_resource)
    return resources
