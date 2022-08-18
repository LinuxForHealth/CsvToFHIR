from importlib.resources import Resource
from typing import Dict, List

from fhir.resources.basic import Basic
from fhir.resources.meta import Meta
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding

from linuxforhealth.csvtofhir.model.csv.basic import BasicCsv
from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []

    incoming_data: BasicCsv = BasicCsv.parse_obj(record)
    
    # Create patient-tokens coding   
    # "code": {
    #    "coding": [
    #         {
    #             "code": "patient-tokens",
    #             "display": "Patient Tokens",
    #             "system": "http://ibm.com/fhir/cdm/CodeSystem/wh-basic-resource-type"
    #         }
    #     ],
    #     "text": "Patient Tokens"
    # }
    code_cc = fhir_utils.get_codeable_concept(
        "http://ibm.com/fhir/cdm/CodeSystem/wh-basic-resource-type",
        "patient-tokens",
        "Patient Tokens",
        "Patient Tokens"
    )
    
    token_cc_system = incoming_data.identifierTypeSystem
    
    # loop through token list and create token identifiers
    identifierList = []
    if incoming_data.tokenList:
        for token in incoming_data.tokenList:
            # tokenList list items are in the form of 
            # ["token_name^<token_value>^system", "token_name^<token_value>^system", token_name^<token_value>^system"]
            tokens = token.split("^")
            token_name = tokens[0]
            token_value = tokens[1]
            token_system = tokens[2]
            token_id = "merative." + token_name
            
            identifier = _build_token_identifier(token_id, token_value, token_system, token_cc_system)
            identifierList.append(identifier)
        
    # create extra token identifer - NYSIIS_Legacy_Hash (if present)
    if incoming_data.NYSIIS_Legacy_Hash != None and incoming_data.NYSIIS_Legacy_Hash != "":
        identifier = _build_token_identifier("NYSIIS_Legacy_Hash", incoming_data.NYSIIS_Legacy_Hash, incoming_data.baseSystem, token_cc_system)
        identifierList.append(identifier)
    
    # create extra token identifer - STD_SSN_Hash (if present)
    if incoming_data.STD_SSN_Hash != None and incoming_data.STD_SSN_Hash != "":
        identifier = _build_token_identifier("STD_SSN_Hash",incoming_data.STD_SSN_Hash, incoming_data.baseSystem, token_cc_system)
        identifierList.append(identifier)
    
    # create other identifier - tokenized_sid
    if incoming_data.tokenized_sid != None and incoming_data.tokenized_sid != "":
        identifier = _build_other_identifier("tokenized_sid", incoming_data.tokenized_sid, incoming_data.baseSystem)
        identifierList.append(identifier)
        
    # create other identifier - token_encryption_key
    if incoming_data.token_encryption_key != None and incoming_data.token_encryption_key != "":
        identifier = _build_other_identifier("token_encryption_key", incoming_data.token_encryption_key, incoming_data.baseSystem)
        identifierList.append(identifier)
        
    # create other identifier - source_patient_sid
    if incoming_data.source_patient_sid != None and incoming_data.source_patient_sid != "":
        identifier = _build_other_identifier("source_patient_sid", incoming_data.tokenized_sid, incoming_data.baseSystem)
        identifierList.append(identifier)
        
    # create other identifier - sid
    if incoming_data.sid != None and incoming_data.sid != "":
        identifier = _build_other_identifier("sid", incoming_data.sid, incoming_data.baseSystem)
        identifierList.append(identifier)
        
    # create basic fhir resource with an id if patientInternalIdentifier is present
    fhir_resource: Basic = Basic.construct(
        id="patient-tokens." + incoming_data.patientInternalIdentifier if incoming_data.patientInternalIdentifier != None and incoming_data.patientInternalIdentifier != "" else None,
        code=code_cc,
        identifier=identifierList
    )
    
    # Add patient subject link if the patientInternalIdentifier is present
    if incoming_data.patientInternalIdentifier != None and incoming_data.patientInternalIdentifier != "":
        patient_reference = fhir_utils.get_resource_reference_from_str(
            "Patient",
            incoming_data.patientInternalIdentifier
        )
        fhir_resource.subject = patient_reference
    
    # Add created date if it's present
    if incoming_data.created_date != None and incoming_data.created_date  != "":
        fhir_resource.created = fhir_utils.get_datetime(incoming_data.created_date)

    resources.append(fhir_resource)
    return resources


# Builds a non token identifier
# { 
#     "id": "<base system>.<code>",    	  # eg "merative.explorys-sid", "datavant.token_encryption_key"
#     "system": "urn:id:merative",          # or "urn:id:datavant"
#     "type": {
#         "coding": [
#             {
#                 "code": "sid",                   # or for datavant: "token_encryption_key", "tokenized_sid", also for explorys "source_patient_sid"
#                 "system": "urn:id:merative"      # or "urn:id:datavant"
#             }
#         ]
#     },
#     "value": "<value>"
# }
def _build_other_identifier(name, value, system):
    
        identifier_type_cc = Coding.construct(
            system=system,
            code=name,
        )
                
        identifier = Identifier.construct(
            id="merative." + name,
            value=str(value),
            system=system,
            type=identifier_type_cc
        )
        
        return identifier
        
# Builds a token identifier
# {
#     "id": "<base system>.<token name>",    # eg "merative.explorys-nysiis", "merative.explorys-ssn", "datavant.token1"
#     "system": "urn:id:merative",           # or "urn:id:datavant"
#     "type": {
#         "coding": [
#             {
#                 "code": "TKN",
#                 "display": "Token identifier",
#                 "system": "http://ibm.com/fhir/cdm/CodeSystem/identifier-type"
#             }
#         ],
#         "text": "Token identifier"
#     },
#     "value": "<token value>"
# },
def _build_token_identifier(token_id, token_value, token_system, token_cc_system):
        
        identifier_type_cc = fhir_utils.get_codeable_concept(
            token_cc_system,
            "TKN",
            "Token identifier",
            "Token identifier"
        )
        
        identifier = Identifier.construct(
            id=token_id,
            value=str(token_value),
            system=fhir_utils.get_uri_format(token_system),
            type=identifier_type_cc
        )
        
        return identifier