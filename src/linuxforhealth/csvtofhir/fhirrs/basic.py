from importlib.resources import Resource
from time import time
from typing import Dict, List

from fhir.resources.basic import Basic
from fhir.resources.meta import Meta
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept

from linuxforhealth.csvtofhir.model.csv.basic import BasicCsv
from linuxforhealth.csvtofhir.fhirutils import fhir_utils


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []

    incoming_data: BasicCsv = BasicCsv.parse_obj(record)
    
    resource_id = None
    if incoming_data.patientInternalIdentifier != None and incoming_data.patientInternalIdentifier != "":
        resource_id = "patient-tokens." + incoming_data.patientInternalIdentifier
    
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
      
    # loop through token list and create token identifiers
    identifierList = []
    if incoming_data.tokenList:
        for token in incoming_data.tokenList:
            # tokenList list items are in the form of 
            # ["token_name^token_value^system", "token_name^token_value^system", token_name^token_value^system"]
            tokens = token.split("^")
            token_name = tokens[0]
            token_value = tokens[1]
            token_system = tokens[2]
            token_id = incoming_data.baseSystem + "." + token_name
            
            # if the value is null then discard this token
            if token_value == "null":
                continue
            
            identifier = _build_token_identifier(token_id, token_value, token_system)
            identifierList.append(identifier)
            
    if incoming_data.otherIdentifierList:
        for other in incoming_data.otherIdentifierList:
            # otherIdentifierList list items are in the form of 
            # ["name^value^system", "name^value^system", name^value^system"]
            parts = other.split("^")
            name = parts[0]
            value = parts[1]
            system = parts[2]
            id = incoming_data.baseSystem + "." + name
            
            # if the value is null then discard this identifier
            if value == "null":
                continue
            
            identifier = _build_other_identifier(id, name, value, system)
            identifierList.append(identifier)
                  
    # Use local copy of resource_meta so changes do not affect other resources
    # Passing in none for the source record id because it is not applicable here
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        None, resource_meta)
    
    # create basic fhir resource with an id if patientInternalIdentifier is present
    fhir_resource: Basic = Basic.construct(
        id=resource_id,
        code=code_cc,
        identifier=identifierList,
        meta=resource_meta_copy
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
        # remove the time part of the date time if it exists
        if " " in incoming_data.created_date:
            time_part_index = incoming_data.created_date.index(" ")
        else:
            time_part_index = len(incoming_data.created_date)
        created_date = incoming_data.created_date[0:time_part_index]
        fhir_resource.created = fhir_utils.get_date(created_date)

    resources.append(fhir_resource)
    return resources


# Builds a non token identifier
# { 
#     "id": <id>
#     "system": <system>
#     "type": {
#         "coding": [
#             {
#                 "code": "<name>",
#                 "system": "<system>"
#             }
#         ]
#     },
#     "value": "<value>"
# }
def _build_other_identifier(id, name, value, system):
    
        identifier_type_cc = CodeableConcept.construct()
        coding = Coding.construct(
            system=fhir_utils.get_uri_format(system),
            code=name
        )
        identifier_type_cc.coding = []
        identifier_type_cc.coding.append(coding)
                
        identifier = Identifier.construct(
            id=id,
            value=str(value),
            system=fhir_utils.get_uri_format(system),
            type=identifier_type_cc
        )
        
        return identifier
        
# Builds a token identifier
# {
#     "id": <id>
#     "system": <system>
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
def _build_token_identifier(token_id, token_value, token_system):
        
        identifier_type_cc = fhir_utils.get_codeable_concept(
            "http://ibm.com/fhir/cdm/CodeSystem/identifier-type",
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