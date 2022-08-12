import datetime

import pytest
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta

from linuxforhealth.csvtofhir.fhirrs import meta
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl
from linuxforhealth.csvtofhir.model.contract import GeneralSection


@pytest.fixture
def general_settings_definition(data_contract_model) -> GeneralSection:
    """
    The file definition used to create a Patient resource

    :param data_contract_model: The DataContract model for resource mapping
    :return: The "Patient" FileDefinition
    """
    return data_contract_model.general


def test_create_meta(general_settings_definition: GeneralSection):
    meta_obj: Meta = meta.create_meta(
        "28008192-filename.csv", "Patient", general_settings_definition.dict()
    )
    assert meta_obj
    assert meta_obj.extension
    assert len(meta_obj.extension) == 5
    ext: Extension
    for ext in meta_obj.extension:
        if ext.url == ExtensionUrl.META_PROCESS_TIMESTAMP_EXTENSION_URL:
            assert ext.valueDateTime
            delta: datetime.timedelta = (
                datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
                - ext.valueDateTime
            )
            assert delta.seconds == 0

        if ext.url == ExtensionUrl.META_SOURCE_EVENT_TRIGGER_EXTENSION_URL:
            assert ext.valueCodeableConcept
            assert ext.valueCodeableConcept.text == "Patient"

        if ext.url == ExtensionUrl.META_SOURCE_FILE_ID_EXTENSION_URL:
            assert ext.valueString == "28008192-filename.csv"

        if ext.url == ExtensionUrl.META_SOURCE_RECORD_TYPE_EXTENSION_URL:
            assert ext.valueCodeableConcept
            assert ext.valueCodeableConcept.text == "csv"

        if ext.url == ExtensionUrl.META_TENANT_ID_EXTENSION_URL:
            assert ext.valueString == "sample-tenant"
