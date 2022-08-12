
from functools import cache

from pydantic import BaseSettings, Field


class ConverterConfig(BaseSettings):
    """
    Contains settings used to bootstrap the converter library.
    """

    csv_buffer_size: int = Field(
        default=1000,
        description="The number of records returned to the converter per iteration"
    )

    mapping_config_directory: str = Field(
        default="/var/app/config",
        description="The directory containing the csvtofhir mapping file"
    )

    mapping_config_file_name: str = Field(
        default="data-contract.json",
        description="The csvtofhir mapping file name."
    )

    @property
    def configuration_path(self):
        """returns the full path to the converter configuration file"""
        # Use forward slashes to ensure consistent on Windows and Linux
        dir_name = self.mapping_config_directory
        if not dir_name.endswith('/'):
            dir_name = dir_name + '/'
        return dir_name + self.mapping_config_file_name


@cache
def get_converter_config() -> "ConverterConfig":
    """Returns the ConverterConfig"""
    return ConverterConfig()
