from importlib.resources import Resource
from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.patient import Patient

from linuxforhealth.csvtofhir.fhirutils import csv_utils, fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import ExtensionUrl
from linuxforhealth.csvtofhir.model.csv.patient import PatientCsv
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []
    pat_name = csv_utils.get_human_name(record)
    patient_name = [pat_name] if pat_name else None

    incoming_patient: PatientCsv = PatientCsv.parse_obj(record)
    if not incoming_patient.contains_patient_data():
        return resources

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_patient.dict())

    patient_id = (
        fhir_utils.format_id_datatype(incoming_patient.patientInternalId)
        if incoming_patient.patientInternalId
        else fhir_utils.format_id_datatype(group_by_key)
    )

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_patient.patientSourceRecordId, resource_meta)

    fhir_patient: Patient = Patient.construct(
        id=fhir_utils.get_resource_id(patient_id),
        name=patient_name,
        identifier=identifiers,
        meta=resource_meta_copy
    )

    fhir_patient.gender = incoming_patient.gender
    fhir_patient.telecom = fhir_utils.get_contact_point_phone(incoming_patient.telecomPhone)

    address = fhir_utils.get_address(
        incoming_patient.address1,
        incoming_patient.address2,
        incoming_patient.city,
        incoming_patient.state,
        incoming_patient.postalCode,
        incoming_patient.country,
        incoming_patient.addressText
    )
    if address:
        fhir_patient.address = [address]

    if incoming_patient.birthDate:
        fhir_patient.birthDate = csv_utils.format_date(incoming_patient.birthDate)

    try:
        if incoming_patient.deceasedDateTime:
            fhir_patient.deceasedDateTime = csv_utils.format_date(incoming_patient.deceasedDateTime)
        # if we didn't set it above, try boolean value
        if not fhir_patient.deceasedDateTime and incoming_patient.deceasedBoolean:
            deceased = fhir_utils.get_boolean_value(incoming_patient.deceasedBoolean)
            if deceased is not None:
                fhir_patient.deceasedBoolean = deceased
    except Exception:
        logger.warning("An exception occurred evaluating Patient resource deceased")
        raise

    try:
        if incoming_patient.multipleBirthBoolean:
            multiple_births = bool(incoming_patient.multipleBirthBoolean)
            fhir_patient.multipleBirthBoolean = multiple_births
        if (
            not fhir_patient.multipleBirthBoolean
            and incoming_patient.multipleBirthInteger
        ):
            fhir_patient.multipleBirthInteger = int(
                incoming_patient.multipleBirthInteger
            )
    except Exception:
        logger.warning("An exception occurred evaluating Patient resource multipleBirth")
        raise

    # extensions
    _add_race_ethnic_extensions(incoming_patient, fhir_patient)
    _add_age_extensions(incoming_patient, fhir_patient)

    resources.append(fhir_patient)
    return resources


def _add_race_ethnic_extensions(incoming_patient: PatientCsv, fhir_patient: Patient):
    """
    Adds race, enthnicity extensions to the patient.
    """
    extension = fhir_utils.get_extension_with_codeable_concept(
        ExtensionUrl.RACE_EXTENSION_SYSTEM,
        incoming_patient.race,
        incoming_patient.raceSystem,
        fhir_constants.PatientResource.race_display.get(incoming_patient.race, None),
        incoming_patient.raceText
    )
    if extension:
        # Add extension to the Patient resource
        if not fhir_patient.extension:
            fhir_patient.extension = []
        fhir_patient.extension.append(extension)

    extension = fhir_utils.get_extension_with_codeable_concept(
        ExtensionUrl.ETHNICITY_EXTENSION_SYSTEM,
        incoming_patient.ethnicity,
        incoming_patient.ethnicitySystem,
        fhir_constants.PatientResource.ethnicity_display.get(incoming_patient.ethnicity, None),
        incoming_patient.ethnicityText
    )
    if extension:
        if not fhir_patient.extension:
            fhir_patient.extension = []
        fhir_patient.extension.append(extension)


def _add_age_extensions(incoming_patient: PatientCsv, fhir_patient: Patient):
    """
    Adds age in months and weeks extensions to the patient.
    """
    # Add patient_age_in_weeks if present
    if (incoming_patient.ageInWeeksForAgeUnder2Years):
        integer_weeks = int(incoming_patient.ageInWeeksForAgeUnder2Years)
        extension = fhir_utils.get_extension(
            ExtensionUrl.PATIENT_AGE_IN_WEEKS_EXTENSION_URL,
            "valueUnsignedInt",
            integer_weeks
        )
        if extension:
            if not fhir_patient.extension:
                fhir_patient.extension = []
            fhir_patient.extension.append(extension)

    # Add patient_age_in_months if present
    if (incoming_patient.ageInMonthsForAgeUnder8Years):
        integer_months = int(incoming_patient.ageInMonthsForAgeUnder8Years)
        extension = fhir_utils.get_extension(
            ExtensionUrl.PATIENT_AGE_IN_MONTHS_EXTENSION_URL,
            "valueUnsignedInt",
            integer_months
        )
        if extension:
            if not fhir_patient.extension:
                fhir_patient.extension = []
            fhir_patient.extension.append(extension)
