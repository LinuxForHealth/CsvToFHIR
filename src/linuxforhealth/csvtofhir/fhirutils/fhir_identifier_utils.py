from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier

from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants

from typing import Union


class IdentifierType:
    SUBSCRIBER_NUMBER = ("SN", "Subscriber Number")
    SOCIAL_SECURITY_NUMBER = ("SS", "Social Security number")
    EMPLOYER_NUMBER = ("EN", "Employer number")
    MEMBER_NUMBER = ("MB", "Member Number")
    NPI_NUMBER = ("NPI", "National provider identifier")
    RESOURCE_IDENTIFIER = ("RI", "Resource identifier")
    PATIENT_INTERNAL_IDENTIFIER = ("PI", "Patient internal identifier")
    MEDICAL_RECORD_NUMBER = ("MR", "Medical record number")
    ACCOUNT_NUMBER = ("AN", "Account number")
    ENCOUNTER_NUMBER = ("VN", "Visit number")
    DRIVERS_LICENSE = ("DL", "Driver's license number")
    PRESCRIPTION_NUMBER = ("RXN", "Prescription Number")


class FIELDS:
    PATIENT_ID = "patientInternalId"
    SSN = "ssn"
    MRN = "mrn"
    ACCOUNT_NUMBER = "accountNumber"
    ENCOUNTER_NUMBER = "encounterNumber"
    RESOURCE_ID = "resourceInternalId"
    ASSIGNING_AUTHORITY = "assigningAuthority"
    DRIVERS_LICENSE = "driversLicense"
    DRIVERS_LICENSE_SYSTEM = "driversLicenseSystem"
    PRACTITIONER_NPI = "identifier_practitionerNPI"
    PRESCRIPTION_NUMBER = "medicationRxNumber"


IDENTIFIER_MAPPING = {
    FIELDS.PATIENT_ID: IdentifierType.PATIENT_INTERNAL_IDENTIFIER,
    FIELDS.SSN: IdentifierType.SOCIAL_SECURITY_NUMBER,
    FIELDS.MRN: IdentifierType.MEDICAL_RECORD_NUMBER,
    FIELDS.ACCOUNT_NUMBER: IdentifierType.ACCOUNT_NUMBER,
    FIELDS.ENCOUNTER_NUMBER: IdentifierType.ENCOUNTER_NUMBER,
    FIELDS.RESOURCE_ID: IdentifierType.RESOURCE_IDENTIFIER,
    FIELDS.DRIVERS_LICENSE: IdentifierType.DRIVERS_LICENSE,
    FIELDS.PRACTITIONER_NPI: IdentifierType.NPI_NUMBER,
    FIELDS.PRESCRIPTION_NUMBER: IdentifierType.PRESCRIPTION_NUMBER,
}

ASSIGNING_AUTHORITY_RECORD_MAPPING = {
    IdentifierType.PATIENT_INTERNAL_IDENTIFIER[0]: FIELDS.ASSIGNING_AUTHORITY,
    IdentifierType.DRIVERS_LICENSE[0]: FIELDS.DRIVERS_LICENSE_SYSTEM,
    IdentifierType.MEDICAL_RECORD_NUMBER[0]: FIELDS.ASSIGNING_AUTHORITY,
    IdentifierType.ACCOUNT_NUMBER[0]: FIELDS.ASSIGNING_AUTHORITY,
    IdentifierType.RESOURCE_IDENTIFIER[0]: FIELDS.ASSIGNING_AUTHORITY,
    IdentifierType.ENCOUNTER_NUMBER[0]: FIELDS.ASSIGNING_AUTHORITY,
    IdentifierType.PRESCRIPTION_NUMBER[0]: FIELDS.ASSIGNING_AUTHORITY,
}

ASSIGNING_AUTHORITY_SYSTEM_FIELD = {
    IdentifierType.SOCIAL_SECURITY_NUMBER[0]: "ssnSystem"
}

IDENTIFIER_TYPE_DEFAULT_SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0203"

IDENTIFIER_TYPE_SYSTEM_OVERWRITE = {
    IdentifierType.PRESCRIPTION_NUMBER[0]: "http://ibm.com/fhir/cdm/CodeSystem/identifier-type"
}

# Identifiers in this list can have multiple instances
# Identifiers not in the list will only be one instance (e.g. NPI, SS)
IDENTIFIER_LIST_ID_INCLUDE_VALUE = [
    IdentifierType.MEDICAL_RECORD_NUMBER[0],
    IdentifierType.DRIVERS_LICENSE[0],
    IdentifierType.ACCOUNT_NUMBER[0],
    IdentifierType.ENCOUNTER_NUMBER[0],
    IdentifierType.PATIENT_INTERNAL_IDENTIFIER[0],
    IdentifierType.RESOURCE_IDENTIFIER[0],
    IdentifierType.PRESCRIPTION_NUMBER[0]
]

# Preferred system(s) to use for external identifiers (urn:id:extID).
# When building an external ID, this controls which coding in the CodeableConcept will be used to build the value.
# - Key is the FHIR resource type.
# - Value is the list of system(s).
#     The system listed first is most preferred, then the second, etc.
EXT_ID_PREFERRED_SYSTEMS = {
    "AllergyIntolerance": [SystemConstants.SNOMED,
                           SystemConstants.ICD10,
                           SystemConstants.ICD9,
                           SystemConstants.LOINC,
                           SystemConstants.NCI,
                           SystemConstants.MESH,
                           SystemConstants.UMLS],
    "Condition": [SystemConstants.ICD10,
                  SystemConstants.ICD9,
                  SystemConstants.SNOMED,
                  SystemConstants.LOINC,
                  SystemConstants.NCI,
                  SystemConstants.MESH,
                  SystemConstants.UMLS],
    "Immunization": [SystemConstants.CVX,
                     SystemConstants.RXNORM,
                     SystemConstants.NDC,
                     SystemConstants.SNOMED,
                     SystemConstants.LOINC,
                     SystemConstants.CPT,
                     SystemConstants.MESH,
                     SystemConstants.NCI,
                     SystemConstants.UMLS],
    "Observation": [SystemConstants.LOINC,
                    SystemConstants.ICD10,
                    SystemConstants.ICD9,
                    SystemConstants.SNOMED,
                    SystemConstants.MESH,
                    SystemConstants.NCI,
                    SystemConstants.UMLS],
    "MedicationRequest": [SystemConstants.RXNORM,
                          SystemConstants.NDC,
                          SystemConstants.SNOMED,
                          SystemConstants.MESH,
                          SystemConstants.NCI,
                          SystemConstants.UMLS],
    "MedicationAdministration": [SystemConstants.RXNORM,
                                 SystemConstants.NDC,
                                 SystemConstants.SNOMED,
                                 SystemConstants.MESH,
                                 SystemConstants.NCI,
                                 SystemConstants.UMLS],
    "MedicationStatement": [SystemConstants.RXNORM,
                            SystemConstants.NDC,
                            SystemConstants.SNOMED,
                            SystemConstants.MESH,
                            SystemConstants.NCI,
                            SystemConstants.UMLS],
    "Procedure": [SystemConstants.CPT,
                  SystemConstants.ICD10PCS,
                  SystemConstants.SNOMED,
                  SystemConstants.NCI,
                  SystemConstants.LOINC,
                  SystemConstants.MESH,
                  SystemConstants.UMLS]
}


def build_extid_identifier(value: str, identifier_id: str = "extID") -> Union[Identifier, None]:
    '''
    Creates an external identifier (with system=urn:id:extId)

    Parms:
    - value: value of the identifier
    - identifier_id: id of the identifier

    Returns the external id FHIR Identifier
    '''
    if value is None:
        return None
    system = "urn:id:extID"
    return Identifier.construct(
        id=fhir_utils.format_id_datatype(identifier_id), value=str(value), system=system
    )


def build_identifier(value, system, type_code_system, type_code, type_code_text=None):
    if value is None:
        return None
    identifier_id = type_code
    if type_code in IDENTIFIER_LIST_ID_INCLUDE_VALUE:
        identifier_id = fhir_utils.format_id_datatype(f"{type_code}.{value}")

    c: Coding = None
    if type_code:
        c = Coding.construct(code=type_code, system=type_code_system, display=type_code_text)
    if c or type_code_text:
        cc = CodeableConcept.construct(coding=[c] if c else None, text=type_code_text)
    return Identifier.construct(
        id=identifier_id,
        value=str(value),
        system=fhir_utils.get_uri_format(system),
        type=cc
    )


def build_identifier_by_type(value, system, id_type: IdentifierType) -> Union[Identifier, None]:
    if value is None:
        return None
    type_code = id_type[0]
    type_code_text = id_type[1]
    type_code_system = (
        IDENTIFIER_TYPE_DEFAULT_SYSTEM
        if type_code not in IDENTIFIER_TYPE_SYSTEM_OVERWRITE
        else IDENTIFIER_TYPE_SYSTEM_OVERWRITE[type_code]
    )
    return build_identifier(
        value,
        system,
        type_code_system,
        type_code,
        type_code_text
    )


def add_identifier(rec: dict, identifiers: list, key: str):
    if key not in rec:
        return
    identifier_key = None if not IDENTIFIER_MAPPING[key] else IDENTIFIER_MAPPING[key][0]
    identifier_value = rec[key]

    if identifier_key in ASSIGNING_AUTHORITY_SYSTEM_FIELD.keys():
        # if this identifier has a sibling field containing the system, get system from that field.
        system = rec.get(ASSIGNING_AUTHORITY_SYSTEM_FIELD[identifier_key], None)
    else:
        system = None

    system_field_name = (
        None
        if identifier_key not in ASSIGNING_AUTHORITY_RECORD_MAPPING.keys()
        else ASSIGNING_AUTHORITY_RECORD_MAPPING[identifier_key]
    )

    if system_field_name and system_field_name in rec and rec[system_field_name]:
        system = rec[system_field_name]  # overwrite

    identifier = build_identifier_by_type(
        identifier_value, system, IDENTIFIER_MAPPING[key]
    )

    if identifier:
        identifiers.append(identifier)


def create_identifier_list(record: dict):
    identifiers: list = []
    for key in IDENTIFIER_MAPPING.keys():
        if key not in record.keys() or not record.get(key) or record.get(key) == 'None':
            continue
        add_identifier(record, identifiers, key)
    return identifiers if identifiers else None
