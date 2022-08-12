from typing import List, Optional
from pydantic import validator

from linuxforhealth.csvtofhir.fhirutils import csv_record_validator as csvrecord
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants, ValueDataAbsentReason
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

DEFAULT_ALLERGY_CODE_SYSTEM = SystemConstants.SNOMED_SYSTEM
DEFAULT_MANIFESTATION_SYSTEM = SystemConstants.SNOMED_SYSTEM

DEFAULT_ALLERGY_CLINICAL_STATUS_CODE = "active"


class AllergyIntoleranceCsv(CsvBaseModel):
    patientInternalId: Optional[str]
    accountNumber: Optional[str]
    ssn: Optional[str]
    ssnSystem: Optional[str]
    mrn: Optional[str]
    encounterInternalId: Optional[str]
    encounterNumber: Optional[str]
    resourceInternalId: Optional[str]
    assigningAuthority: Optional[str]

    allergySourceRecordId: Optional[str]

    allergyCategory: Optional[str]
    allergyType: Optional[str]
    allergyRecordedDateTime: Optional[str]

    allergyCode: Optional[str]
    allergyCodeSystem: Optional[str] = DEFAULT_ALLERGY_CODE_SYSTEM
    allergyCodeText: Optional[str]

    allergyCriticality: Optional[str]

    allergyManifestationCode: Optional[str]
    allergyManifestationSystem: Optional[str] = DEFAULT_MANIFESTATION_SYSTEM
    allergyManifestationText: Optional[str]
    allergyManifestationCodeList: Optional[List[str]]

    allergyClinicalStatusCode: Optional[str]

    allergyVerificationStatusCode: Optional[str]

    allergyOnsetStartDateTime: Optional[str]
    allergyOnsetEndDateTime: Optional[str]

    @validator("ssn")
    def validate_ssn(cls, v):
        return csvrecord.validate_ssn(v)

    @validator("allergyCodeSystem", always=True)
    def validate_allergyCodeSystem(cls, v):
        if v:
            return v
        return DEFAULT_ALLERGY_CODE_SYSTEM

    @validator("allergyManifestationSystem", always=True)
    def validate_allergyManifestationSystem(cls, v):
        if v:
            return v
        return DEFAULT_MANIFESTATION_SYSTEM

    def has_reaction_data(self) -> bool:
        return any(
            [
                self.allergyManifestationCode,
                self.allergyManifestationText
            ]
        ) or (self.allergyManifestationCodeList and len(self.allergyManifestationCodeList) > 0)

    def get_allergy_manifestation_cc_list(self):
        manifestation_cc_list = []
        # input may be a single code/system and/or a list of code/systems
        # first, try the single code/system
        manifestation_cc = fhir_utils.get_codeable_concept(
            self.allergyManifestationSystem,
            self.allergyManifestationCode,
            None,
            self.allergyManifestationText
        )
        if manifestation_cc:
            manifestation_cc_list.append(manifestation_cc)
        if self.allergyManifestationCodeList is not None:
            for manifestation_hl7 in self.allergyManifestationCodeList:
                manifestation_cc_list.append(fhir_utils.add_hl7_style_codeable_concept(manifestation_hl7))
        if len(manifestation_cc_list) > 0:
            return manifestation_cc_list
        # if no single code and no list of code, set to unknown
        return fhir_utils.get_coding(
            ValueDataAbsentReason.CODE_UNKNOWN[0],
            ValueDataAbsentReason.SYSTEM,
            ValueDataAbsentReason.CODE_UNKNOWN[1]
        )
