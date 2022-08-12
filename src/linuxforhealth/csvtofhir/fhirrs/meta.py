from datetime import datetime, timezone

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta

from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl


def create_meta(
    file_name: str, mapped_resource_type: str, general_directives: dict
) -> Meta:
    meta: Meta = Meta.construct()
    meta.extension = []

    ext_tenant_id: Extension = Extension.construct(url=ExtensionUrl.META_TENANT_ID_EXTENSION_URL)
    ext_tenant_id.valueString = general_directives.get("tenantId")
    meta.extension.append(ext_tenant_id)

    ext_source_file_id: Extension = Extension.construct(
        url=ExtensionUrl.META_SOURCE_FILE_ID_EXTENSION_URL
    )
    ext_source_file_id.valueString = file_name
    meta.extension.append(ext_source_file_id)

    ext_source_event_trigger: Extension = Extension.construct(
        url=ExtensionUrl.META_SOURCE_EVENT_TRIGGER_EXTENSION_URL
    )
    ext_source_event_trigger.valueCodeableConcept = CodeableConcept.construct(
        text=mapped_resource_type
    )
    meta.extension.append(ext_source_event_trigger)

    ext_process_timestamp: Extension = Extension.construct(
        url=ExtensionUrl.META_PROCESS_TIMESTAMP_EXTENSION_URL
    )
    ext_process_timestamp.valueDateTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    meta.extension.append(ext_process_timestamp)

    ext_source_record_type: Extension = Extension.construct(
        url=ExtensionUrl.META_SOURCE_RECORD_TYPE_EXTENSION_URL
    )
    ext_source_record_type.valueCodeableConcept = fhir_utils.get_codeable_concept(None, None, None, "csv")
    meta.extension.append(ext_source_record_type)

    return meta
