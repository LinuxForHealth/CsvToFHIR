from typing import Optional
from pydantic import validator

from fhir.resources.codeableconcept import CodeableConcept

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ConditionResource, SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.support import get_logger

DEFAULT_CONDITION_CODE_SYSTEM = SystemConstants.SNOMED_SYSTEM
DEFAULT_CONDITION_SEVERITY_SYSTEM = SystemConstants.SNOMED_SYSTEM

CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS = "encounter-diagnosis"
CONDITION_CATEGORY_PROBLEM_LIST = "problem-list-item"


logger = get_logger(__name__)


class ConditionCsv(CsvBaseModel):
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]
    encounterInternalId: Optional[str]
    encounterNumber: Optional[str]
    resourceInternalId: Optional[str]
    assigningAuthority: Optional[str]
    conditionSourceRecordId: Optional[str]

    encounterClaimType: Optional[str]

    conditionCategory: Optional[str]
    conditionRecordedDateTime: Optional[str]
    conditionOnsetDateTime: Optional[str]
    conditionAbatementDateTime: Optional[str]
    conditionClinicalStatus: Optional[str]
    conditionVerificationStatus: Optional[str]

    # only used when category=diagnosis-condition; not used for problem-list-item
    conditionDiagnosisRank: Optional[str]
    # use / role(s) of the diagnosis in the encounter
    conditionPrincipalDiagnosis: Optional[str]
    conditionRoleIsAdmitting: Optional[str]
    conditionRoleIsChiefComplaint: Optional[str]

    conditionCode: Optional[str]
    conditionCodeSystem: Optional[str] = DEFAULT_CONDITION_CODE_SYSTEM
    conditionCodeText: Optional[str]
    conditionSeverityCode: Optional[str]
    conditionSeveritySystem: Optional[str] = DEFAULT_CONDITION_SEVERITY_SYSTEM
    conditionSeverityText: Optional[str]
    # "chronic", "acute" currently mapped to snomed; other values will be placed in text only
    conditionChronicity: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csv_record_validator.validate_ssn(v)

    @validator("conditionCodeSystem")
    def validate_conditionCodeSystem(cls, v):
        if v:
            return v
        return DEFAULT_CONDITION_CODE_SYSTEM

    @validator("conditionSeveritySystem")
    def validate_conditionSeveritySystem(cls, v):
        if v:
            return v
        return DEFAULT_CONDITION_SEVERITY_SYSTEM

    def has_encounter_data(self) -> bool:
        # For Condition resources, we want to create an Encounter to hold the diagnosis or reasonReference link
        # to the Condition -- for this reason the encounterInternalId is enough to create the Encounter even if there
        # is no other Encounter data.  Note that if there is no encounterInternalId we do not create an Encounter
        # in this case, since not having an Encounter.id would result in an
        # 'orphaned' skeleton Encounter that is not useful.
        if self.encounterInternalId or self.encounterClaimType or self.conditionRoleIsAdmitting or \
           self.conditionRoleIsChiefComplaint or self.conditionDiagnosisRank:
            return True
        return False

    def get_condition_category_cc(self) -> CodeableConcept:
        if not self.conditionCategory and self.conditionDiagnosisRank:
            self.conditionCategory = CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS

        if self.conditionCategory == CONDITION_CATEGORY_PROBLEM_LIST:
            return fhir_utils.get_codeable_concept(
                SystemConstants.CONDITION_CATEGORY_SYSTEM,
                CONDITION_CATEGORY_PROBLEM_LIST,
                ConditionResource.category_display.get(CONDITION_CATEGORY_PROBLEM_LIST)
            )

        if self.conditionCategory == CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS:
            return fhir_utils.get_codeable_concept(
                SystemConstants.CONDITION_CATEGORY_SYSTEM,
                CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS,
                ConditionResource.category_display.get(CONDITION_CATEGORY_ENCOUNTER_DIAGNOSIS)
            )

        return None

    def get_encounter_diagnosis_rank_int(self):
        if self.conditionDiagnosisRank:
            try:
                return int(self.conditionDiagnosisRank)
            except ValueError:
                logger.warning("Unable to parse condition diagnosis rank as an integer")
                return None
        return None
