from typing import Optional
from pydantic import Field, validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel


class PatientCsv(CsvBaseModel):
    patientInternalId: Optional[str] = Field(
        description="Patient Internal Id within the source system. Added to resource.identifier as type 'PI' "
                    "Patient Internal id will be also used as (resource.id). "
                    "Restriction on characters: [A-Za-z0-9\\-\\.]{1,64}."
                    "All illegal characters will be replaced with '.' (example Hello!Id -> Hello.Id) "
                    "Specified AssigningAuthority field will be added to this identifier."
    )
    accountNumber: Optional[str] = Field(
        description="Patient Account Number. Should be unique for patient."
        "Added to resource.identifier as type 'AN'. "
        "It is expected that patient might have more than one account number associated with their identity."
        "Specified AssigningAuthority field will be added to this identifier.")
    ssn: Optional[str] = Field(
        description="Patient Social Security Number. Should be unique for a patient. "
        "Added to resource.identifier as type 'SS'."
        "Dashes will be removed. Must contain 9 integers."
        "System source: ssnSystem added in data-contract is used, None if not provided."
        "Social Security numbers that repeat the same number will be set to None (ex. 000-00-0000, 999-99-9999).")
    ssnSystem: Optional[str]
    patientSourceRecordId: Optional[str]
    driversLicense: Optional[str]
    driversLicenseSystem: Optional[str]
    mrn: Optional[str]
    assigningAuthority: Optional[str]
    nameFirst: Optional[str]
    nameFirstMiddle: Optional[str]
    nameMiddle: Optional[str]
    nameLast: Optional[str]
    nameFirstMiddleLast: Optional[str]
    prefix: Optional[str]
    suffix: Optional[str]
    birthDate: Optional[str]
    deceasedDateTime: Optional[str]
    deceasedBoolean: Optional[str]
    multipleBirthBoolean: Optional[str]
    multipleBirthInteger: Optional[int]
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postalCode: Optional[str]
    country: Optional[str]
    addressText: Optional[str]
    telecomPhone: Optional[str]
    race: Optional[str]
    raceSystem: Optional[str] = SystemConstants.RACE_SYSTEM
    raceText: Optional[str]
    ethnicity: Optional[str]
    ethnicitySystem: Optional[str] = SystemConstants.ETHNICITY_SYSTEM
    ethnicityText: Optional[str]
    gender: Optional[str]
    ageInWeeksForAgeUnder2Years: Optional[str]
    ageInMonthsForAgeUnder8Years: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("raceSystem", always=True)
    def validate_raceSystem(cls, v):
        if v:
            return v
        return SystemConstants.RACE_SYSTEM

    @validator("ethnicitySystem", always=True)
    def validate_ethnicitySystem(cls, v):
        if v:
            return v
        return SystemConstants.ETHNICITY_SYSTEM

    def contains_patient_data(self) -> bool:
        # At least one of these fields must be present to build a Patient, otherwise do not build.
        # These are the only important fields.
        fields = [
            self.ssn,
            self.driversLicense,
            self.mrn,
            self.nameFirst,
            self.nameFirstMiddle,
            self.nameMiddle,
            self.nameLast,
            self.nameFirstMiddleLast,
            self.prefix,
            self.suffix,
            self.birthDate,
            self.deceasedDateTime,
            self.deceasedBoolean,
            self.multipleBirthBoolean,
            self.multipleBirthInteger,
            self.address1,
            self.address2,
            self.city,
            self.state,
            self.postalCode,
            self.country,
            self.addressText,
            self.telecomPhone,
            self.race,
            self.ethnicity,
            self.gender
        ]
        return any(fields)
