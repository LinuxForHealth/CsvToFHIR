from typing import List, Optional
from pydantic import BaseModel, Field, validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants, ValueDataAbsentReason
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

ENCOUNTER_STATUS_DEFAULT_VALUE = "unknown"
ENCOUNTER_CLASS_CODING_SYSTEM = SystemConstants.ENCOUNTER_CLASS_CODING_SYSTEM


class EncounterStatusHistoryEntry(BaseModel):
    status: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]


class EncounterCsv(CsvBaseModel):
    patientInternalId: Optional[str] = Field(
        description="Patient Internal Id within the source system. Added to resource.identifier as type 'PI' "
        "Patient Internal id will be also used as (resource.id). "
        "Restriction on characters: [A-Za-z0-9\\-\\.]{1,64}."
        "All illegal characters will be replaced with '-' (example Hello!Id -> Hello-Id) "
        "Specified AssigningAuthority field will be added to this identifier."
    )
    accountNumber: Optional[str] = Field(
        description="Patient Account Number. Should be unique for patient."
        "Added to resource.identifier as type 'AN'. "
        "It is expected that patient might have more than one account number associated with their identity."
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
    assigningAuthority: Optional[str]
    encounterSourceRecordId: Optional[str]

    encounterStatus: Optional[str] = ENCOUNTER_STATUS_DEFAULT_VALUE
    encounterClassCode: Optional[str]
    encounterClassText: Optional[str]
    encounterClassSystem: Optional[str] = SystemConstants.ENCOUNTER_CLASS_CODING_SYSTEM

    encounterPriorityCode: Optional[str]
    encounterPriorityText: Optional[str]
    encounterPriorityCodeSystem: Optional[str] = SystemConstants.PRIORITY_SYSTEM

    encounterStartDateTime: Optional[str]
    encounterEndDateTime: Optional[str]
    encounterLengthValue: Optional[str]
    encounterLengthUnits: Optional[str]
    encounterReasonCode: Optional[str]
    encounterReasonCodeSystem: Optional[str]
    encounterReasonCodeText: Optional[str]

    # hospitalization section within Encounter
    hospitalizationAdmitSourceCode: Optional[str]
    hospitalizationAdmitSourceCodeText: Optional[str]
    hospitalizationAdmitSourceCodeSystem: Optional[str] = SystemConstants.ADMISSION_SOURCE_SYSTEM

    hospitalizationReAdmissionCode: Optional[str]
    hospitalizationReAdmissionCodeText: Optional[str]
    hospitalizationReAdmissionCodeSystem: Optional[str]
    hospitalizationDischargeDispositionCode: Optional[str]
    hospitalizationDischargeDispositionCodeText: Optional[str]
    hospitalizationDischargeDispositionCodeSystem: Optional[str] = SystemConstants.DISCHARGE_DISPOSITION_SYSTEM

    # participant section within Encounter
    encounterParticipantSequenceId: Optional[str]
    encounterParticipantTypeCode: Optional[str]
    encounterParticipantTypeText: Optional[str]
    encounterParticipantTypeCodeSystem: Optional[str] = SystemConstants.PARTICIPANT_TYPE_SYSTEM

    practitionerInternalId: Optional[str]
    practitionerNPI: Optional[str]
    practitionerNameLast: Optional[str]
    practitionerNameFirst: Optional[str]
    practitionerGender: Optional[str]
    practitionerRoleText: Optional[str]
    practitionerRoleCodes: Optional[str]
    practitionerRoleCodesSystem: Optional[str]
    practitionerSpecialtyCodes: Optional[str]
    practitionerSpecialtyCodesSystem: Optional[str]
    practitionerSpecialtyText: Optional[str]

    # location section within Encounter
    encounterLocationSequenceId: Optional[str]
    encounterLocationPeriodStart: Optional[str]
    encounterLocationPeriodEnd: Optional[str]
    locationResourceInternalId: Optional[str]
    locationName: Optional[str]
    locationTypeCode: Optional[str]
    locationTypeText: Optional[str]
    locationTypeCodeSystem: Optional[str]

    # status history is an array of strings.
    # with each string representing status history status^start_date^end_date
    encounterStatusHistory: Optional[List[str]]

    # Extension: Insured
    encounterInsuredEntryId: Optional[str]
    encounterInsuredRank: Optional[int]
    encounterInsuredCategoryCode: Optional[str]
    encounterInsuredCategorySystem: Optional[str]
    encounterInsuredCategoryText: Optional[str]

    # Extension: Claim-type
    encounterClaimType: Optional[str]

    # Extension: drgCode
    encounterDrgCode: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("encounterStatus", always=True)
    def validate_encounterStatus(cls, v):
        if v:
            return v
        return ENCOUNTER_STATUS_DEFAULT_VALUE

    @validator("encounterClassSystem", always=True)
    def validate_encounterClassSystem(cls, v):
        if v:
            return v
        return ENCOUNTER_CLASS_CODING_SYSTEM

    @validator("hospitalizationAdmitSourceCodeSystem", always=True)
    def validate_hospitalizationAdmitSourceCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.ADMISSION_SOURCE_SYSTEM

    @validator("hospitalizationDischargeDispositionCodeSystem", always=True)
    def validate_hospitalizationDischargeDispositionCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.DISCHARGE_DISPOSITION_SYSTEM

    @validator("encounterParticipantTypeCodeSystem", always=True)
    def validate_encounterParticipantTypeCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.PARTICIPANT_TYPE_SYSTEM

    @validator("encounterPriorityCodeSystem", always=True)
    def validate_encounterPriorityCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.PRIORITY_SYSTEM

    # Order indicates Primary, Secondary, Tertiary, etc.. it is a good entry id to allow overwriting values
    # However, user has an option to provide a different id
    def get_insured_entry_id(self):
        if any([self.encounterInsuredRank, self.encounterInsuredEntryId]):
            return (
                self.encounterInsuredEntryId
                if self.encounterInsuredEntryId
                else self.encounterInsuredRank
            )
        return (
            self.encounterInsuredCategoryCode
            if self.encounterInsuredCategoryCode
            else self.encounterInsuredCategoryText
        )

    def get_drg_code(self):
        return self.encounterDrgCode

    def get_required_field_encounter_class(self):
        if self.encounterClassCode:  # Encounter Class is set
            return fhir_utils.get_coding(
                self.encounterClassCode,
                self.encounterClassSystem,
                self.encounterClassText
            )

        # set to temporarily unknown codeable concept
        return fhir_utils.get_coding(
            ValueDataAbsentReason.CODE_TEMPORARILY_UNKNOWN[0],
            ValueDataAbsentReason.SYSTEM,
            ValueDataAbsentReason.CODE_TEMPORARILY_UNKNOWN[1]
        )

    def contains_hospitalization_entries(self) -> bool:
        """
        Return True if any of the hospitalization fields are set/active
        otherwise returns False to make sure hospitalization segment in the encounter stays as None
        """
        return any(
            [
                self.hospitalizationAdmitSourceCode,
                self.hospitalizationAdmitSourceCodeText,
                self.hospitalizationReAdmissionCode,
                self.hospitalizationReAdmissionCodeText,
                self.hospitalizationDischargeDispositionCode,
                self.hospitalizationDischargeDispositionCodeText
            ]
        )
