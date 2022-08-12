from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

DEFAULT_OBSERVATION_STATUS = "unknown"


class ObservationCsv(CsvBaseModel):
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]
    encounterNumber: Optional[str]
    encounterInternalId: Optional[str]
    resourceInternalId: Optional[str]
    assigningAuthority: Optional[str]
    observationSourceRecordId: Optional[str]
    observationStatus: Optional[str]
    observationCategory: Optional[str]
    observationDateTime: Optional[str]
    practitionerNPI: Optional[str]
    practitionerInternalId: Optional[str]
    observationCode: Optional[str]
    observationCodeSystem: Optional[str]
    observationCodeText: Optional[str]
    observationCodeList: Optional[List[str]]
    observationValue: Optional[str]
    observationValueUnits: Optional[str]
    observationValueDataType: Optional[str]
    observationRefRange: Optional[str]
    observationRefRangeLow: Optional[str]
    observationRefRangeHigh: Optional[str]
    observationRefRangeText: Optional[str]
    observationInterpretationCode: Optional[str]
    observationInterpretationCodeSystem: Optional[str] = SystemConstants.OBSERVATION_INTERPRETATION_SYSTEM
    observationInterpretationCodeDisplay: Optional[str]
    observationInterpretationCodeText: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("observationStatus", always=True)
    def validate_observationStatus(cls, v):
        if v:
            return v
        return DEFAULT_OBSERVATION_STATUS

    @validator("observationInterpretationCodeSystem", always=True)
    def validate_observationInterpretationCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.OBSERVATION_INTERPRETATION_SYSTEM
