from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.support import get_logger

RESOURCE_TYPE_MED_ADMINISTRATION = "MedicationAdministration"
RESOURCE_TYPE_MED_REQUEST = "MedicationRequest"
RESOURCE_TYPE_MED_STATEMENT = "MedicationStatement"

MEDICATION_ADMINISTRATION_DEFAULT_STATUS = "unknown"
MEDICATION_REQUEST_DEFAULT_STATUS = "unknown"
MEDICATION_STATEMENT_DEFAULT_STATUS = "unknown"
MEDICATION_REQUEST_DEFAULT_INTENT = "order"

logger = get_logger(__name__)


class MedicationUseCsv(CsvBaseModel):
    # If not specified generic resource will be used
    resourceType: Optional[str] = RESOURCE_TYPE_MED_STATEMENT
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]
    medicationSourceRecordId: Optional[str]
    encounterInternalId: Optional[str]
    encounterNumber: Optional[str]
    encounterClaimType: Optional[str]
    encounterClassCode: Optional[str]
    resourceInternalId: Optional[str]
    medicationRxNumber: Optional[str]
    assigningAuthority: Optional[str]

    medicationUseStatus: Optional[str]
    medicationUseCategoryCode: Optional[str]
    medicationUseCategoryCodeSystem: Optional[str]
    medicationUseCategoryCodeText: Optional[str]
    medicationUseStartedOn: Optional[str]
    medicationUseOccuranceDateTime: Optional[str]

    medicationCode: Optional[str]
    medicationCodeDisplay: Optional[str]
    medicationCodeSystem: Optional[str]
    medicationCodeText: Optional[str]
    '''
    Each string in the list is formatted as a set of up to 3 values separated by carets (^).
        - code^display^system
    The system can be a full URL for a shortname for the URL from SystemConstants.CodingSystemURLs
    Examples:
        - 1115005^^http://www.nlm.nih.gov/research/umls/rxnorm
        - 1115005
        - 0904-7183-61^Docusate Sodium^NDC
    '''
    medicationCodeList: Optional[List[str]]

    medicationUseRouteCode: Optional[str]
    medicationUseRouteCodeSystem: Optional[str]
    medicationUseRouteText: Optional[str]
    medicationUseRouteList: Optional[List[str]]

    medicationUseDosageText: Optional[str]
    medicationUseDosageValue: Optional[str]
    medicationUseDosageUnit: Optional[str]

    # These used in MedicationRequest
    medicationValidityStart: Optional[str]
    medicationValidityEnd: Optional[str]
    medicationRefills: Optional[str]
    medicationQuantity: Optional[str]
    medicationAuthoredOn: Optional[str]
    medicationRequestIntent: Optional[str] = MEDICATION_REQUEST_DEFAULT_INTENT

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    def contains_dosage_entries(self) -> bool:
        """
        Return True if any of the route or dosage fields are set/active.
        """
        return any(
            [
                self.medicationUseRouteCode,
                self.medicationUseRouteText,
                self.medicationUseDosageText,
                self.medicationUseDosageValue
            ]
        )

    def get_default_category_system(self):
        if self.resourceType == RESOURCE_TYPE_MED_ADMINISTRATION:
            return SystemConstants.MED_ADM_CATEGORY_SYSTEM
        if self.resourceType == RESOURCE_TYPE_MED_REQUEST:
            return SystemConstants.MED_REQ_CATEGORY_SYSTEM
        if self.resourceType == RESOURCE_TYPE_MED_STATEMENT:
            return SystemConstants.MED_STM_CATEGORY_SYSTEM

        msg = f"resource type {self.resourceType} does not have a default category system code mapping"
        logger.warning(msg)
        return None
