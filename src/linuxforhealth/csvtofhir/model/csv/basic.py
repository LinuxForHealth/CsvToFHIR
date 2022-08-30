from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.model.csv.base import BaseModel


class IdentifierDetails(BaseModel):
    name: Optional[str]
    value: Optional[str]
    system: Optional[str]

class BasicCsv(CsvBaseModel):
    baseSystem: Optional[str]                  # base system
    tokenList: Optional[List[str]]             # token identifier list
    patientInternalIdentifier: Optional[str]   # id
    created_date: Optional[str]                # created date
    otherIdentifierList: Optional[List[str]]   # non-token identifiers