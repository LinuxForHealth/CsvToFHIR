from typing import List, Optional
from pydantic import Field, validator

from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel

PRACTITIONER_TAXONOMY_DEFAULT_SYSTEM = SystemConstants.PROVIDER_TAXONOMY_SYSTEM


class PractitionerCsv(CsvBaseModel):
    assigningAuthority: Optional[str]
    resourceInternalId: Optional[str] = Field(
        alias="practitionerInternalId",
        description='resourceInternalId is used to setup resource.id as well as resource.identifier of type "RI"'
    )
    identifier_practitionerNPI: Optional[str] = Field(
        alias="practitionerNPI",
        description="Use identifier_practionerNPI if NPI needs to be placed into identifiers list of the resources"
    )
    practitionerNameLast: Optional[str]
    practitionerNameFirst: Optional[str]
    # practitionerNameText is only used if practitionerNameLast is not specified, otherwise it is ignored / discarded
    practitionerNameText: Optional[str]
    practitionerGender: Optional[str]
    practitionerRoleText: Optional[str]
    practitionerRoleCode: Optional[str]
    practitionerRoleCodeList: Optional[List[str]]
    practitionerRoleCodeSystem: Optional[str]
    practitionerSpecialtyCode: Optional[str]
    practitionerSpecialtyCodeList: Optional[List[str]]
    practitionerSpecialtyCodeSystem: Optional[str] = PRACTITIONER_TAXONOMY_DEFAULT_SYSTEM
    practitionerSpecialtyText: Optional[str]

    @validator("practitionerSpecialtyCodeSystem")
    def validate_practitionerSpecialtyCodeSystem(cls, v):
        if v:
            return v
        return PRACTITIONER_TAXONOMY_DEFAULT_SYSTEM

    class Config:
        allow_population_by_field_name = False

    def contains_practitioner_role_data(self) -> bool:
        # these are important fields to require PractitionerRole
        fields = [
            self.practitionerRoleText,
            self.practitionerRoleCode,
            self.practitionerRoleCodeList,
            self.practitionerSpecialtyText,
            self.practitionerSpecialtyCode,
            self.practitionerSpecialtyCodeList
        ]
        return any(fields)

    def contains_practitioner_data(self) -> bool:
        # these are fields that might warrant Practitioner resource to be created
        # PractitionerRole will not be sufficient
        fields = [
            self.practitionerNameLast,
            self.practitionerNameFirst,
            self.practitionerGender
        ]
        # create only if we have some physician demographics or
        # if practitioner role data is not available,
        # but we still have resourceInternalId (practionerInternalId) to deal with)
        if any(fields):
            return True

        # If NPI or internal Id needs to be reported and it will NOT be reported via PractitionerRole
        # then create practitioner
        if self.resourceInternalId or self.identifier_practitionerNPI:
            return not self.contains_practitioner_role_data()

        return False
