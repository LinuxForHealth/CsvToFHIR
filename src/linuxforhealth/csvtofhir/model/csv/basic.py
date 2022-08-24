from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.model.csv.base import BaseModel


class IdentifierDetails(BaseModel):
    token_name: Optional[str]
    token_value: Optional[str]
    token_system: Optional[str]

class BasicCsv(CsvBaseModel):
    identifierTypeSystem: Optional[str]        # system for token identifiers
    baseSystem: Optional[str]                  # base system
    identifierNamePrefix: Optional[str]        # prefix for identifier ids
    tokenList: Optional[List[str]]             # token identifier list
    patientInternalIdentifier: Optional[str]   # id
    created_date: Optional[str]                # subject
    otherIdentifierList: Optional[List[str]]   # non-token identifiers