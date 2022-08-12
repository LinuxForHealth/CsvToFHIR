import datetime
from typing import Dict
import dateutil.parser as dtparser
from fhir.resources.humanname import HumanName

from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.support import get_logger, is_valid_year

logger = get_logger(__name__)


class HumanNameFields:
    LAST = "nameLast"
    FIRST = "nameFirst"
    MIDDLE = "nameMiddle"
    FIRST_MIDDLE = "nameFirstMiddle"
    FIRST_MIDDLE_LAST = "nameFirstMiddleLast"
    PREFIX = "namePrefix"
    SUFFIX = "nameSuffix"


def get_human_name(csvrecord: dict) -> HumanName:
    if not csvrecord:
        return None

    prefix: str = (
        None
        if HumanNameFields.PREFIX not in csvrecord
        else csvrecord[HumanNameFields.PREFIX]
    )
    suffix: str = (
        None
        if HumanNameFields.SUFFIX not in csvrecord
        else csvrecord[HumanNameFields.SUFFIX]
    )

    last: str = (
        None
        if HumanNameFields.LAST not in csvrecord
        else csvrecord[HumanNameFields.LAST]
    )
    first: str = (
        None
        if HumanNameFields.FIRST not in csvrecord
        else csvrecord[HumanNameFields.FIRST]
    )
    middle: str = (
        None
        if HumanNameFields.MIDDLE not in csvrecord
        else csvrecord[HumanNameFields.MIDDLE]
    )

    if last and not first and HumanNameFields.FIRST_MIDDLE in csvrecord:
        first_middle_last = csvrecord[HumanNameFields.FIRST_MIDDLE] + "  " + last
        return fhir_utils.get_fhir_human_name_from_fml_string(first_middle_last, prefix, suffix)

    if last:  # Last Name found
        return fhir_utils.get_fhir_human_name(last, first, middle, prefix, suffix)

    if (
        HumanNameFields.FIRST_MIDDLE_LAST in csvrecord
        and csvrecord[HumanNameFields.FIRST_MIDDLE_LAST]
    ):
        return fhir_utils.get_fhir_human_name_from_fml_string(
            csvrecord[HumanNameFields.FIRST_MIDDLE_LAST], prefix, suffix
        )

    return None


def format_date(
    date_data: str, format_directives: Dict = None, format_key: str = None
) -> str:
    # special case of year only (4 digits in range), return
    # further processing assumes a full date and behavior for missing month or day is not defined.
    if is_valid_year(date_data):
        return date_data

    try:
        parsed_date = dtparser.parse(date_data)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        logger.warning("Unable to parse date")
        if (
            not format_directives
            or format_key not in format_directives
            or not format_directives[format_key]
        ):
            return None

    # try to use supplied format
    dt = datetime.datetime.strptime(date_data, format_directives[format_key])
    if dt:
        dt.strftime("%Y-%m-%d")
