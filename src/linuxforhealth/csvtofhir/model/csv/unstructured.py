from typing import Optional
from pydantic import Field, validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

RESOURCE_TYPE_DIAG_REPORT = "DiagnosticReport"
RESOURCE_TYPE_DOC_REFERENCE = "DocumentReference"
RESOURCE_STATUS_DEFAULT = "current"
DOCUMENT_TYPE_CODING_SYSTEM = SystemConstants.LOINC_SYSTEM


def get_default_document_code(resource_type: str):
    if resource_type == RESOURCE_TYPE_DIAG_REPORT:
        code = "50398-7"
        text = "Narrative diagnostic report [Interpretation]"
    else:
        code = "67781-5"
        text = "Summarization of encounter note Narrative"
    return fhir_utils.get_codeable_concept(DOCUMENT_TYPE_CODING_SYSTEM, code, text)


class UnstructuredCsv(CsvBaseModel):
    resourceType: Optional[str] = RESOURCE_TYPE_DOC_REFERENCE
    patientInternalId: Optional[str] = Field(
        description="Patient Internal Id within the source system. Added to resource.identifier as type 'PI' "
        "Patient Internal id will be also used as (resource.id). "
        "Restriction on characters: [A-Za-z0-9\\-\\.]{1,64}."
        "All illegal characters will be replaced with '.' (example Hello!Id -> Hello.Id) "
        "Specified AssigningAuthority field will be added to this identifier."
    )
    accountNumber: Optional[str] = Field(
        description="Patient Account Number. Should be unique for patient."
        "Added to resource.identifier as type 'AN'. "
        "It is expected that patient might have more than one account number associated with their identity, "
        "while Patient Internal Id does not. "
        "Specified AssigningAuthority field will be added to this identifier."
    )
    ssn: Optional[str] = Field(
        description="Patient Social Security Number. Should be unique for a patient. "
        "Added to resource.identifier as type 'SS'."
        "Dashes will be removed. Must contain 9 integers"
        "System source: ssnSystem added in data-contract is used, None if not provided."
        "Social Security numbers that repeat the same number will be set to None (ex. 000-00-0000, 999-99-9999)."
    )
    ssnSystem: Optional[str]
    mrn: Optional[str]
    encounterNumber: Optional[str] = Field(
        description="Encounter or Visit Number. "
        "Combined with AssigningAuthority column to create a unique encounter within the system"
    )

    resourceInternalId: Optional[str]
    encounterInternalId: Optional[str]
    assigningAuthority: Optional[str]

    resourceStatus: Optional[str] = RESOURCE_STATUS_DEFAULT
    documentStatus: Optional[str]
    documentTypeCode: Optional[str]
    documentTypeCodeSystem: Optional[str] = DOCUMENT_TYPE_CODING_SYSTEM
    documentTypeCodeText: Optional[str]
    documentDateTime: Optional[str]

    documentAttachmentContentType: Optional[str]
    documentAttachmentContent: Optional[str]
    documentAttachmentTitle: Optional[str]

    practitionerInternalId: Optional[str]
    practitionerNPI: Optional[str]
    practitionerNameLast: Optional[str]
    practitionerNameFirst: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("resourceStatus", always=True)
    def validate_resource_status(cls, v):
        if v:
            return v
        return RESOURCE_STATUS_DEFAULT

    @validator("resourceType", always=True)
    def validate_resource_type(cls, v):
        if v not in [RESOURCE_TYPE_DOC_REFERENCE, RESOURCE_TYPE_DIAG_REPORT]:
            return RESOURCE_TYPE_DOC_REFERENCE
        return v

    @validator("documentTypeCodeSystem", always=True)
    def validate_document_type_code_system(cls, v):
        if v:
            return v
        return DOCUMENT_TYPE_CODING_SYSTEM
