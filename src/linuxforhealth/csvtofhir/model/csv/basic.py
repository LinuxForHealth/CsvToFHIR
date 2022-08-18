from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants, ValueDataAbsentReason
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.model.csv.base import BaseModel


class TokenDetails(BaseModel):
    token_name: Optional[str]
    token_value: Optional[str]
    token_system: Optional[str]

class BasicCsv(CsvBaseModel):
    identifierTypeSystem: Optional[str]        # system for token identifiers
    baseSystem: Optional[str]                  # base system
    tokenList: Optional[List[str]]             # token identifiers
    patientInternalIdentifier: Optional[str]   # id
    # datavant
    token_encryption_key: Optional[str]        # other identifier
    tokenized_sid: Optional[str]               # other identifier
    source_patient_sid: Optional[str]          # other identifier
    created_date: Optional[str]                # subject
    # explorys
    sid: Optional[str]                         # other identifier
    NYSIIS_Legacy_Hash: Optional[str]          # token identifier
    STD_SSN_Hash: Optional[str]                # token identifier