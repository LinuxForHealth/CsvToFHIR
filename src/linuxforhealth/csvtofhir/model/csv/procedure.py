import re
from typing import List, Optional, Union
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

DEFAULT_STATUS = "unknown"


class ProcedureCsv(CsvBaseModel):
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]

    procedureSourceRecordId: Optional[str]
    encounterInternalId: Optional[str]
    encounterNumber: Optional[str]
    encounterClaimType: Optional[str]

    resourceInternalId: Optional[str]
    assigningAuthority: Optional[str]

    procedureStatus: Optional[str]
    procedurePerformedDateTime: Optional[str]

    procedureCategory: Optional[str]
    procedureCategorySystem: Optional[str]
    procedureCategoryText: Optional[str]

    procedureCode: Optional[str]
    procedureCodeSystem: Optional[str]
    procedureCodeDisplay: Optional[str]
    procedureCodeText: Optional[str]
    procedureCodeList: Optional[List[str]]

    procedureModifierList: Optional[str]
    procedureModifierSystem: Optional[str]

    procedureEncounterSequenceId: Optional[str]

    practitionerInternalId: Optional[str]
    practitionerNPI: Optional[str]
    practitionerNameLast: Optional[str]
    practitionerNameFirst: Optional[str]
    practitionerGender: Optional[str]
    practitionerRoleText: Optional[str]
    practitionerRoleCode: Optional[str]
    practitionerRoleCodeSystem: Optional[str]
    practitionerSpecialtyCode: Optional[str]
    practitionerSpecialtyCodeSystem: Optional[str]
    practitionerSpecialtyText: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("procedureStatus", always=True)
    def validate_procedureStatus(cls, v):
        if v:
            return v
        return DEFAULT_STATUS

    def has_encounter_data(self) -> bool:
        return any(
            [
                self.encounterInternalId,
                self.encounterNumber,
                self.procedureEncounterSequenceId
            ]
        )

    def get_modifier_list(self) -> Union[list, None]:
        if not self.procedureModifierList:
            return None
        if isinstance(self.procedureModifierList, list):
            return self.procedureModifierList
        if not isinstance(self.procedureModifierList, str):
            return None
        modifier_list = self.procedureModifierList.strip()
        if modifier_list.isalnum():
            modifiers = [
                modifier_list[i: i + 2] for i in range(0, len(modifier_list), 2)
            ]
        else:
            modifiers = [x for x in re.split("[\\s,;]", modifier_list) if x]
        return modifiers
