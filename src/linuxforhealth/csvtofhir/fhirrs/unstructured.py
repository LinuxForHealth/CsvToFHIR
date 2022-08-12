from typing import Dict, List

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import (DocumentReference,
                                              DocumentReferenceContent,
                                              DocumentReferenceContext)
from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import practitioner
from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.model.csv import unstructured
from linuxforhealth.csvtofhir.model.csv.unstructured import (RESOURCE_TYPE_DIAG_REPORT,
                                                             RESOURCE_TYPE_DOC_REFERENCE,
                                                             UnstructuredCsv)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    incoming_data: UnstructuredCsv = UnstructuredCsv.parse_obj(record)

    if incoming_data.resourceType not in [
        RESOURCE_TYPE_DOC_REFERENCE,
        RESOURCE_TYPE_DIAG_REPORT
    ]:
        incoming_data.resourceType = RESOURCE_TYPE_DOC_REFERENCE  # default

    attachment = fhir_utils.get_attachment_object(
        incoming_data.documentAttachmentContentType,
        incoming_data.documentAttachmentContent,
        incoming_data.documentAttachmentTitle,
        incoming_data.documentDateTime
    )
    if not attachment:
        return []  # not valid request

    identifiers = fhir_identifier_utils.create_identifier_list(record)

    patient_reference = fhir_utils.get_resource_reference_from_str(
        "Patient",
        fhir_utils.get_resource_id(
            incoming_data.patientInternalId
            if incoming_data.patientInternalId
            else group_by_key
        ),
    )

    code_cc: CodeableConcept = None
    if incoming_data.documentTypeCode:
        code_cc = fhir_utils.get_codeable_concept(
            incoming_data.documentTypeCodeSystem,
            incoming_data.documentTypeCode,
            incoming_data.documentTypeCodeText
        )
    else:
        code_cc = unstructured.get_default_document_code(incoming_data.resourceType)

    if attachment.creation:  # do not create identifier if do not have a document date
        # Build extId using the code for document type plus the document date
        value = code_cc.coding[0].code + "-" + attachment.creation.isoformat()
        ext_id = fhir_identifier_utils.build_extid_identifier(value)
        identifiers.append(ext_id)

    encounter_reference = fhir_utils.get_resource_reference_from_str(
        "Encounter", incoming_data.encounterInternalId
    )

    practitioner_resources = practitioner.convert_record(
        group_by_key, record, resource_meta
    )

    resources: list[Resource] = []
    practitioner_reference: list = None
    if practitioner_resources:
        resources.extend(practitioner_resources)
        practitioner_reference = fhir_utils.get_resource_reference(
            practitioner_resources[0]
        )

    if incoming_data.resourceType == RESOURCE_TYPE_DIAG_REPORT:
        document_resource = DiagnosticReport.construct(
            id=fhir_utils.get_resource_id(incoming_data.resourceInternalId),
            status=incoming_data.documentStatus,
            identifier=identifiers,
            subject=patient_reference,
            code=code_cc,
            meta=resource_meta,
            issued=fhir_utils.get_instance(incoming_data.documentDateTime),
            encounter=encounter_reference,
            resultsInterpreter=[practitioner_reference]
            if practitioner_reference
            else None,
            presentedForm=[attachment]
        )
    else:
        dr_content: DocumentReferenceContent = DocumentReferenceContent.construct(
            attachment=attachment
        )
        document_resource = DocumentReference.construct(
            id=fhir_utils.get_resource_id(incoming_data.resourceInternalId),
            status=incoming_data.resourceStatus,
            docStatus=incoming_data.documentStatus,
            identifier=identifiers,
            subject=patient_reference,
            type=code_cc,
            meta=resource_meta,
            date=fhir_utils.get_instance(incoming_data.documentDateTime),
            context=DocumentReferenceContext.construct(encounter=[encounter_reference]),
            author=[practitioner_reference] if practitioner_reference else None,
            content=[dr_content]
        )

    if document_resource:
        resources.append(document_resource)
    return resources
