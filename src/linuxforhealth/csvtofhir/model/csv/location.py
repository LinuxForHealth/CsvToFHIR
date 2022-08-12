from typing import Optional
from pydantic import Field, validator

from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel


class LocationCsv(CsvBaseModel):
    assigningAuthority: Optional[str]
    resourceInternalId: Optional[str] = Field(
        alias="locationResourceInternalId",
        description='resourceInternalId is used to setup resource.id as well as resource.identifier of type "RI"'
    )
    locationName: Optional[str]
    locationTypeCode: Optional[str]
    locationTypeText: Optional[str]
    locationTypeCodeSystem: Optional[str] = SystemConstants.LOCATION_TYPE_SYSTEM

    @validator("locationTypeCodeSystem")
    def validate_locationTypeCodeSystem(cls, v):
        if v:
            return v
        return SystemConstants.LOCATION_TYPE_SYSTEM

    def contains_location_data(self) -> bool:
        # These fields are important enough to require Location, otherwise do not build Location resource.
        fields = [
            self.resourceInternalId,
            self.locationName,
            self.locationTypeCode,
            self.locationTypeText
        ]
        return any(fields)
