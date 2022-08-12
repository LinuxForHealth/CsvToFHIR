from typing import Optional

from pydantic import Field

from linuxforhealth.csvtofhir.model.csv.base import CsvBaseModel


class OrganizationCsv(CsvBaseModel):
    # NOTE: minimally needs Name or Identifier
    assigningAuthority: Optional[str]
    resourceInternalId: Optional[str] = Field(
        alias="organizationResourceInternalId",
        description='resourceInternalId is used to setup resource.id as well as resource.identifier of type "RI"'
    )
    organizationName: Optional[str]

    def contains_organization_data(self) -> bool:
        # these are fields that might warrant Organization resource to be created to preserve data
        fields = [
            self.organizationName,
        ]
        if any(fields):
            return True

        return False
