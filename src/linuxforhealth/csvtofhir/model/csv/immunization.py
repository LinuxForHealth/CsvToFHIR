from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


class ImmunizationCsv(CsvBaseModel):
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]
    resourceInternalId: Optional[str]
    assigningAuthority: Optional[str]

    immunizationSourceRecordId: Optional[str]
    immunizationDoseQuantity: Optional[str]
    immunizationDoseUnit: Optional[str]
    immunizationDoseText: Optional[str]
    encounterNumber: Optional[str]
    encounterInternalId: Optional[str]
    organizationResourceInternalId: Optional[str]
    organizationName: Optional[str]  # manufacturer
    immunizationRouteCode: Optional[str]
    immunizationRouteSystem: Optional[str] = SystemConstants.SNOMED_SYSTEM
    immunizationRouteText: Optional[str]
    immunizationSiteCode: Optional[str]
    immunizationSiteSystem: Optional[str] = SystemConstants.SNOMED_SYSTEM
    immunizationSiteText: Optional[str]
    immunizationStatus: Optional[str]  # completed | entered-in-error | not-done
    immunizationStatusReasonCode: Optional[str]
    immunizationStatusReasonSystem: Optional[str]
    immunizationStatusReasonText: Optional[str]
    immunizationVaccineCode: Optional[str]
    immunizationVaccineSystem: Optional[str] = SystemConstants.CVX_SYSTEM
    immunizationVaccineDisplay: Optional[str]
    immunizationVaccineText: Optional[str]
    '''
    Each string in the list is formatted as a set of up to 3 values separated by carets (^).
        - code^display^system
    The system can be a full URL for a shortname for the URL from SystemConstants.CodingSystemURLs
    Examples:
        - 1115005^^http://www.nlm.nih.gov/research/umls/rxnorm
        - 1115005
        - 8948^Purified Protein Derivative of Tuberculin^RXNORM
    '''
    immunizationVaccineCodeList: Optional[List[str]]
    immunizationDate: Optional[str]  # immunization_date
    immunizationExpirationDate: Optional[str]  # immunization_expiration_date

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("immunizationVaccineSystem", always=True)
    def validate_immunizationVaccineSystem(cls, v):
        if v:
            return v
        return SystemConstants.CVX_SYSTEM

    @validator("immunizationSiteSystem", always=True)
    def validate_immunizationSiteSystem(cls, v):
        if v:
            return v
        return SystemConstants.SNOMED_SYSTEM

    @validator("immunizationRouteSystem", always=True)
    def validate_immunizationRouteSystem(cls, v):
        if v:
            return v
        return SystemConstants.SNOMED_SYSTEM
