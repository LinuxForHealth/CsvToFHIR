import base64
import copy
import pytz
import re
import time
import uuid
from datetime import datetime
from pydantic.datetime_parse import parse_datetime
from typing import Optional, Union
from urllib.parse import urlparse

from fhir.resources.address import Address
from fhir.resources.attachment import Attachment
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.duration import Duration
from fhir.resources.extension import Extension
from fhir.resources.fhirtypes import Instant, parse_date
from fhir.resources.humanname import HumanName
from fhir.resources.meta import Meta
from fhir.resources.period import Period
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirutils import fhir_identifier_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl, SystemConstants
from linuxforhealth.csvtofhir.support import get_logger

DEFAULT_CONTENT_TYPE = "text/plain"

logger = get_logger(__name__)


def is_boolean_value(value: str) -> bool:
    """
    Returns True if the string input matches boolean string values
    """
    # Handle case where input is None
    if value is None:
        return False
    return value.lower() in ["true", "false", "t", "f"]


def get_boolean_value(value: str) -> Union[bool, None]:
    """
    Returns a boolean mapping of boolean string values to Boolean
    Returns None if input not a valid boolean string
    """
    # Handle case where input is None
    if value is None:
        return None
    # Must be in our set of values.  "NotBoolean" is not False but rather None
    elif is_boolean_value(value):
        return value.lower() in ["true", "t"]
    else:
        return None


def is_valid_decimal(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def format_id_datatype(id_string: str) -> Union[str, None]:
    if not id_string:
        return None
    return re.sub(r"[^A-Za-z0-9\-\.]", "-", str(id_string).strip())


def get_resource_id(id=None) -> str:
    if not id:
        now_ns = time.time_ns()
        uuid_string = uuid.uuid4().hex
        return str(f"{now_ns}.{uuid_string}")
    return format_id_datatype(id)


def get_new_bundle() -> Bundle:
    b = Bundle.construct()
    b.type = "transaction"
    b.id = get_resource_id()
    b.entry = []
    return b


def get_new_bundle_entry(
        request_method_code, request_url, fhir_resource
) -> BundleEntry:
    entry = BundleEntry.construct()
    entry.resource = fhir_resource
    entry.fullUrl = "{0}/{1}".format(fhir_resource.resource_type, fhir_resource.id)
    entry.request = BundleEntryRequest.construct(
        method=request_method_code, url=request_url
    )
    return entry


def get_new_bundle_entry_put_resource(fhir_resource: Resource) -> BundleEntry:
    return get_new_bundle_entry(
        "PUT", fhir_resource.resource_type + "/" + fhir_resource.id, fhir_resource
    )


def get_codeable_concept(system: str, code: str, display: str, text: str = None) \
        -> Optional[CodeableConcept]:
    '''
    This version sets the text to the display if text=None
    '''
    cc = get_codeable_concept_no_text_default(system, code, display, text)
    if cc:
        cc.text = display if text is None else text
    return cc


def get_codeable_concept_no_text_default(system: str, code: str, display: str, text: str = None) \
        -> Optional[CodeableConcept]:
    '''
    This version does not change the text
    '''
    cc = CodeableConcept.construct()
    if text:  # need if to cover case when is an empty string, do not want to copy
        cc.text = text
    if code or display:
        coding = Coding.construct(
            system=get_code_system(system),
            code=code,
            display=display
        )
        cc.coding = []
        cc.coding.append(coding)
    if cc.text or code or display:
        return cc
    return None


def add_hl7_style_codeable_concept(code_data):
    '''
    Creates the codeable concept from <code>^<display>^<system>^<text> form.
    :param coded_list: An entry in the form of <code>^<display>^<system>^<text>
    :return: the created codeable concept
    '''
    code_data = code_data.split("^")
    num_segments = len(code_data)
    the_code = code_data[0]  # first piece is the code
    if not the_code:
        the_code = None
    the_code_display = code_data[1] if num_segments > 1 else None  # second piece is the display
    if not the_code_display:
        the_code_display = None
    the_code_system = code_data[2] if num_segments > 2 else None  # third piece is the system
    if not the_code_system:
        the_code_system = None
    the_text = code_data[3] if num_segments > 3 else None  # fourth piece is the text
    if not the_text:
        the_text = None
    cc = get_codeable_concept(the_code_system, the_code, the_code_display, the_text)
    return cc


def add_hl7_style_coded_list_to_codeable_concept(coded_list, collector_cc=None, custom_system: str = None):
    '''
    Adds entries from a list of <code>^<display>^<system> sets to a codeable concept.
    Creates the codeable concept if one is not passed in.

    :param coded_list: A list of entries set in the form <code>^<display>^<system>
    :param collector_cc: Optional existing codeable concept. If not passed, one is created.
    :param custom_system: Optional, if the system is not set in the entry, this will be used ("urn:id:<custom_system>")
    :return: the updated (or created) codeable concept
    '''
    if coded_list is None:
        return collector_cc
    for code_entry in coded_list:
        # entries are formatted as in HL7: <code>^<display>^<system>
        code_data = code_entry.split("^")
        num_segments = len(code_data)
        the_code = code_data[0]  # first piece is the code
        if not the_code:
            the_code = None
        the_code_display = code_data[1] if num_segments > 1 else None  # second piece is the display
        if the_code_display == "":
            the_code_display = None
        the_code_system = code_data[2] if num_segments > 2 else None  # third piece is the system
        if custom_system and not the_code_system:
            the_code_system = custom_system
        if the_code_system is not None:
            if the_code_system == "":
                the_code_system = None
            else:
                the_code_system = get_code_system(the_code_system)
        collector_cc = add_codeable_concept(collector_cc, the_code_system, the_code, the_code_display)
    return collector_cc


def add_codeable_concept(
    cc: CodeableConcept, system: str, code: str, display: str
) -> CodeableConcept:
    '''
    Adds a coding to a CodeableConcept, if it already exists (cc parm is not None).

    If the parm cc is None, the CodeableConcept is created using the data in the other parms.
    '''
    if cc is None:
        return get_codeable_concept_no_text_default(system, code, display)

    if code or display:
        coding = Coding.construct(
            system=get_uri_format(system),
            code=code,
            display=display
        )
        if cc.coding is None:
            cc.coding = []
        if not is_coding_present_in_codeable_concept(coding, cc):
            cc.coding.append(coding)
    # return cc because it may have content.  (Case None handled above)
    return cc


def is_coding_present_in_codeable_concept(test_coding, codeable_concept):
    for existing_coding in codeable_concept.coding:
        if test_coding == existing_coding:
            return True
    return False


def get_coding(code: str = None, system: str = None, display: str = None):
    if not code and not system and not display:
        return None
    return Coding.construct(system=system, code=code, display=display)


def add_source_record_id_return_meta_copy(source_record_id: str, resource_meta: Meta) -> Meta:
    """
    Sets source_record_id extension in the resource meta if one is provided. If no Meta is provided one is created.
    Returns a copy of the appended Meta because the Meta may be global and it should only be changed at initialization
    for the file.
    By returning a copy, we also avoid potential data bleed.
    :param source_record_id: the source_record_id to add
    :param resource_meta: the Meta object to append
    """
    # if no source_record_id, return the meta we were given
    if source_record_id is None:
        return resource_meta
    # if no Meta given, create Meta shell
    if resource_meta is None:
        resource_meta = Meta.construct()
        resource_meta.extension = []

    resource_meta_copy = copy.deepcopy(resource_meta)

    # if the source_record_id is already present, then replace the value.
    # Add our source_record_id to the Meta
    ext_source_file_id: Extension = Extension.construct(
        url=ExtensionUrl.META_SOURCE_RECORD_ID_EXTENSION_URL
    )
    ext_source_file_id.valueString = source_record_id
    resource_meta_copy.extension.append(ext_source_file_id)

    return resource_meta_copy


def get_resource_reference(
        fhir_resource: Resource, display_value: str = None, reference_id: str = None
) -> Union[Reference, None]:
    if not fhir_resource:
        return None
    ref: Reference = Reference.construct(id=format_id_datatype(reference_id))
    ref.reference = "{0}/{1}".format(fhir_resource.resource_type, fhir_resource.id)
    if display_value:
        ref.display = display_value
    elif fhir_resource.resource_type == "Practitioner" and fhir_resource.name:
        ref.display = fhir_resource.name[0].text
    elif (fhir_resource.resource_type == "Organization" or fhir_resource.resource_type == "Location") \
            and fhir_resource.name:
        ref.display = fhir_resource.name
    return ref


def get_resource_reference_from_str(
        resource_type: str, resource_id: str, display_value: str = None
) -> Union[Reference, None]:
    if not resource_type or not resource_id:
        return None
    ref: Reference = Reference.construct()
    ref.reference = "{0}/{1}".format(resource_type, format_id_datatype(resource_id))
    if display_value:
        ref.display = display_value
    return ref


def get_extension(extension_url, valuefield, value):
    if not value:  # do not create extension if it has no value
        return None
    ext: dict = {"url": extension_url, valuefield: value}
    extension: Extension = Extension.parse_obj(ext)
    return extension


def get_extension_with_codeable_concept(
        extension_url, code, coding_system, display=None, text=None
) -> Union[Extension, None]:
    if not code and not text:
        return None
    codeable_concept = get_codeable_concept(coding_system, code, display, text)
    extension: Extension = Extension.construct(url=extension_url)
    extension.valueCodeableConcept = codeable_concept
    return extension


def get_fhir_human_name(
        last: str, first: str, middle: str = None, prefix: str = None, suffix: str = None
) -> Union[HumanName, None]:
    if last is None:
        return None  # there really should be a last name

    human_name = HumanName.construct(
        family=last,
        prefix=[prefix] if prefix else None,
        suffix=[suffix] if suffix else None
    )
    if first is not None:
        human_name.given = [first]
    if middle is not None:
        human_name.given.append(middle)

    text = " ".join(human_name.given) + " " + human_name.family
    human_name.text = (
        ((prefix + " ") if prefix else "") + text + ((" " + suffix) if suffix else "")
    )
    return human_name


def get_fhir_human_name_from_fml_string(
        fml: str, prefix: str = None, suffix: str = None
) -> Union[HumanName, None]:
    name_array = re.split("[;,\\s]+", fml)
    fields_count = len(name_array)
    if fields_count <= 0:
        return None
    last = name_array.pop()
    human_name = HumanName.construct(
        family=last,
        given=name_array if name_array else None,
        prefix=[prefix] if prefix else None,
        suffix=[suffix] if suffix else None
    )
    text = " ".join(human_name.given) + " " + human_name.family
    human_name.text = (
        ((prefix + " ") if prefix else "") + text + ((" " + suffix) if suffix else "")
    )
    return human_name


def get_date(date_time_period):
    return parse_date(date_time_period)


def get_condition_category(condition_category):
    if not condition_category:
        return
    return [
        get_codeable_concept(
            SystemConstants.CONDITION_CATEGORY_SYSTEM,
            condition_category[0],
            condition_category[1]
        )
    ]


def get_address(
        address1: str,
        address2: str,
        city: str,
        state: str,
        postal_code: str,
        country: str = None,
        address_text: str = None
) -> Union[Address, None]:
    if not any([address1, address2, city, state, postal_code, country, address_text]):
        return None
    line = []
    if address1:
        line.append(address1)
    if address2:
        line.append(address2)

    return Address.construct(
        line=line,
        city=city,
        state=state,
        postalCode=postal_code,
        country=country,
        tex=address_text
    )


def get_contact_point_phone(phone_value):
    if phone_value:
        return [ContactPoint.construct(system="phone", value=phone_value)]
    return None


def get_quantity_object(value, unit):
    if value and is_valid_decimal(value):
        return Quantity.construct(value=float(value), unit=unit)
    return None


def get_duration(value, unit):
    if not value:
        return None

    return Duration.construct(value=value, unit=unit)


def get_attachment_object(
        content_type: str, data: str, title, creation_dt
) -> Union[Attachment, None]:
    if not data:
        return None

    # ensure there is a content_type
    the_content_type = content_type if content_type else DEFAULT_CONTENT_TYPE

    a: Attachment = Attachment.construct(
        contentType=the_content_type,
        title=title,
        data=base64.b64encode(data.encode("utf-8"))
    )
    if creation_dt:
        a.creation = parse_datetime(creation_dt)
    return a


def get_datetime(value: str, tzone: str = None):
    if not value:
        return None
    try:
        dt = parse_datetime(value)
        if dt.tzname() is None and tzone is not None:
            tzone = pytz.timezone(tzone)
            dt = tzone.localize(dt)
        return dt
    except BaseException:
        logger.warning("Unable to parse datetime {value}")
        return None


def get_fhir_type_period(start: str, end: str, tzone: str = None) -> Union[Period, None]:
    if not any([start, end]):
        return None
    p: Period = Period.construct()
    if start:
        p.start = get_datetime(start, tzone)
    if end:
        p.end = get_datetime(end, tzone)
    return p


def get_instance(documentDateTime):
    i: Instant = get_datetime(documentDateTime)
    return i


def get_code_system(system: str):
    '''
    - If the input is a shortname (eg "ICD9"), returns the full URL
    - Formats the system correctly, prepending ext:id if needed
    '''
    if system in SystemConstants.CodingSystemURLs.keys():
        # system is the short name, replace with URL
        return SystemConstants.CodingSystemURLs[system]
    return get_uri_format(system)


def get_external_identifier(cc: CodeableConcept, fhir_resource_type: str,
                            fhir_resource=None) -> Union[Extension, None]:
    '''
    Creates an external identifier (used with system=urn:id:extId)

    Parms
    - cc: CodeableConcept used to build the identifier value
    - fhir_resource_type: type of FHIR resource this identifier is being created for
    - fhir_resource: fhir resource to build the identifier for, only required for Observation resources

    Returns
    - extID Identifier
    '''
    if not cc:
        return None
    preferred_system_list = fhir_identifier_utils.EXT_ID_PREFERRED_SYSTEMS.get(fhir_resource_type)
    # get code based on preferred system found above
    preferred_coding = _get_preferred_coding(preferred_system_list, cc.coding)
    if not preferred_coding:
        if cc.text:
            value = cc.text
        else:
            return None
    else:
        value = preferred_coding.code
        if value and preferred_coding.system:  # Have a value and a system
            abbreviated_system = SystemConstants.SystemURLsToCodeShortname.get(preferred_coding.system)
            if abbreviated_system:
                value = f'{value}-{abbreviated_system}'
            else:
                system = preferred_coding.system.lstrip("urn:id:")
                value = f'{value}-{system}'
        elif not value and preferred_coding.display:  # no value but have a display
            value = preferred_coding.display
        # else have a code but no system, will use code for the value

    # Add timestamp for Observation resources, using format YYYYMMDDHHMMSS
    if fhir_resource_type == "Observation":
        # Use resource value, fallback to meta
        timestamp = None
        if fhir_resource.effectiveDateTime:
            timestamp = fhir_resource.effectiveDateTime
        elif fhir_resource.meta and fhir_resource.meta.extension:
            for ext in fhir_resource.meta.extension:
                if "process-timestamp" in ext.url:
                    timestamp = ext.valueDateTime
                    break
        if not timestamp:
            timestamp = datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
        value = f'{timestamp_str}-{value}'

    return fhir_identifier_utils.build_extid_identifier(value)


def _get_preferred_coding(preferred_system_list, codings) -> Union[None, Coding]:
    if not codings:
        return None

    # Look in preferred systems list
    if preferred_system_list:
        for preferred_system in preferred_system_list:
            for coding in codings:
                system_short_name = SystemConstants.SystemURLsToCodeShortname.get(coding.system)
                if coding.system == preferred_system or system_short_name == preferred_system:
                    return coding

    # Fall back to a coding with an unrecognized or unranked (not in preferred system list) system
    for coding in codings:
        if coding.system:
            return coding

    # Last resort is a coding without a system.  At this point there should be no entries with a system,
    # so just take the first entry.
    return codings[0]


def _validate_uri(value: str):
    try:
        result = urlparse(value)
        return result.scheme
    except BaseException:
        logger.warning("Unable to validate uri. Invalid uri")
        return False


def get_uri_format(value: str) -> Union[str, None]:
    if not value:
        return None
    if _validate_uri(value):
        return value
    return f"urn:id:{value}"
