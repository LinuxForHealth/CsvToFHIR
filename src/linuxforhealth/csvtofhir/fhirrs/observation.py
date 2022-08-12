from typing import Dict, List

from fhir.resources.meta import Meta
from fhir.resources.observation import Observation, ObservationReferenceRange
from fhir.resources.patient import Patient
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import practitioner
from linuxforhealth.csvtofhir.fhirutils import fhir_constants, fhir_identifier_utils, fhir_utils
from linuxforhealth.csvtofhir.fhirutils.fhir_constants import SystemConstants
from linuxforhealth.csvtofhir.model.csv.observation import ObservationCsv
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def _set_observation_value(fhir_resource: Observation, incoming_data: ObservationCsv):
    value_data_type = incoming_data.observationValueDataType
    value = incoming_data.observationValue

    # this should never happen because the caller should not try to create the Observation if no value
    if value is None:
        return

    if not value_data_type:  # not assigned from the data contract definitions (try to find the best fitting one)
        value_data_type = _get_observation_value_data_type(incoming_data)

    if value_data_type == "valueQuantity":
        # requires value to be decimal
        if fhir_utils.is_valid_decimal(value):
            fhir_resource.valueQuantity = fhir_utils.get_quantity_object(
                incoming_data.observationValue, incoming_data.observationValueUnits
            )
            return
    elif value_data_type == "valueInteger":
        if value.isnumeric():
            fhir_resource.valueInteger = int(incoming_data.observationValue)
            return
    elif value_data_type == "valueBoolean":
        if fhir_utils.is_boolean_value(value):
            fhir_resource.valueBoolean = fhir_utils.get_boolean_value(incoming_data.observationValue)
            return
    elif value_data_type == "valueCodeableConcept":
        fhir_resource.valueCodeableConcept = fhir_utils.add_hl7_style_codeable_concept(value)
        return

    # Default to String for now
    if incoming_data.observationValueUnits:
        fhir_resource.valueString = f'{incoming_data.observationValue} {incoming_data.observationValueUnits}'
    else:
        fhir_resource.valueString = incoming_data.observationValue


def _get_observation_value_data_type(incoming_data: ObservationCsv) -> str:
    value = incoming_data.observationValue

    # other ca
    if incoming_data.observationValueUnits:
        return "valueQuantity"  # quantity allows to preserve the units in Quantity structure
    elif '^' in incoming_data.observationValue:
        return "valueCodeableConcept"
    elif value.isnumeric():
        return "valueInteger"
    elif fhir_utils.is_valid_decimal(value):
        return "valueQuantity"
    elif fhir_utils.is_boolean_value(value):
        return "valueBoolean"


def _set_observation_reference_range(
        fhir_resource: Observation, incoming_data: ObservationCsv
):
    """
    There is an option to provide observationRefRangeText AND either observationRefRange (format low-high) or
    separate values for Low and High.
    ObservationRefRangeText is always added to "text" field.
    If ObservationRefRangeText is not present, observationRefRange will be added to text in addition to being split
    in low/high values.
    Low and High can be taken directly from the named columns if present.
    Otherwise, an attempt to break observationRefRange value into low and high will be performed.
    """

    # do not set empty reference range, we need at least one field to be specified with value
    if not any(
            [
                incoming_data.observationRefRange,
                incoming_data.observationRefRangeHigh,
                incoming_data.observationRefRangeLow,
                incoming_data.observationRefRangeText
            ]
    ):
        return

    # Automatically set Reference Range Text if it is provided
    ref_range: ObservationReferenceRange = ObservationReferenceRange.construct(
        text=incoming_data.observationRefRangeText
    )

    obs_low = incoming_data.observationRefRangeLow
    obs_high = incoming_data.observationRefRangeHigh
    obs_range = incoming_data.observationRefRange
    if obs_range:
        if not ref_range.text:
            ref_range.text = obs_range

        range_split = obs_range.split("-")
        if len(range_split) == 2:
            if not obs_low:
                obs_low = range_split[0]
            if not obs_high:
                obs_high = range_split[1]

    try:
        ref_range.low = fhir_utils.get_quantity_object(obs_low, incoming_data.observationValueUnits)
        low_range_text = 'low: ' + str(obs_low)

        ref_range.high = fhir_utils.get_quantity_object(obs_high, incoming_data.observationValueUnits)
        high_range_text = 'high: ' + str(obs_high)

        # if text was not set and either low or high value does not convert to a numeric but the original was non-null
        # ref_range.low and ref_range.high will be None if they do not convert to numeric
        # obs_low and obs_high contain the original value
        if not ref_range.text and ((not ref_range.low and obs_low) or (not ref_range.high and obs_high)):
            ref_range.text = low_range_text + ' ' + high_range_text

    except Exception:
        logger.warning("Exception occurred calculating observation range")
        raise

    fhir_resource.referenceRange = [ref_range]


def _set_observation_interpretation(
        fhir_resource: Observation, incoming_data: ObservationCsv
):
    # do not set interpretation if at least one of the following fields does not have a value
    if not any(
            [
                incoming_data.observationInterpretationCode,
                incoming_data.observationInterpretationCodeText
            ]
    ):
        return

    if incoming_data.observationInterpretationCodeDisplay:
        interpretation_display = incoming_data.observationInterpretationCodeDisplay
    elif incoming_data.observationInterpretationCodeSystem == SystemConstants.OBSERVATION_INTERPRETATION_SYSTEM:
        # Only want to look up and set display if its from our default system
        interpretation_display = fhir_constants.ObservationResource.interpretation_code_display.get(
            incoming_data.observationInterpretationCode,
            None)
    else:
        interpretation_display = None

    interpretation = fhir_utils.get_codeable_concept(
        incoming_data.observationInterpretationCodeSystem,
        incoming_data.observationInterpretationCode,
        interpretation_display,
        incoming_data.observationInterpretationCodeText)
    fhir_resource.interpretation = [interpretation]


def convert_record(
        group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    resources: list = []
    incoming_data: ObservationCsv = ObservationCsv.parse_obj(record)

    # Cannot create resource without information for observation.code
    if not incoming_data.observationCode and not incoming_data.observationCodeText:
        return resources  # Empty list

    identifiers = fhir_identifier_utils.create_identifier_list(incoming_data.dict())
    resource_id = (
        fhir_utils.format_id_datatype(incoming_data.resourceInternalId) if incoming_data.resourceInternalId else None
    )

    if incoming_data.observationCode and '^' in incoming_data.observationCode:
        obs_code = fhir_utils.add_hl7_style_codeable_concept(incoming_data.observationCode)
    else:
        obs_code = fhir_utils.get_codeable_concept(
            incoming_data.observationCodeSystem,
            incoming_data.observationCode,
            None,
            incoming_data.observationCodeText
        )

    obs_code = fhir_utils.add_hl7_style_coded_list_to_codeable_concept(
        incoming_data.observationCodeList, obs_code, incoming_data.assigningAuthority)

    # only creating patient reference, assume it's created elsewhere
    if incoming_data.patientInternalId:
        patient = Patient.construct(id=fhir_utils.format_id_datatype(incoming_data.patientInternalId))
    else:
        patient = Patient.construct(id=fhir_utils.format_id_datatype(group_by_key))

    encounter_reference = fhir_utils.get_resource_reference_from_str(
        "Encounter", incoming_data.encounterInternalId
    )

    # Use local copy of resource_meta so changes do not affect other resources
    resource_meta_copy = fhir_utils.add_source_record_id_return_meta_copy(
        incoming_data.observationSourceRecordId, resource_meta)

    fhir_resource: Observation = Observation.construct(
        id=fhir_utils.get_resource_id(resource_id),
        identifier=identifiers,
        status=incoming_data.observationStatus,
        code=obs_code,
        subject=fhir_utils.get_resource_reference(patient),
        encounter=encounter_reference,
        meta=resource_meta_copy
    )
    if (incoming_data.observationCategory and
            incoming_data.observationCategory in fhir_constants.ObservationResource.category_display.keys()):
        category = fhir_utils.get_codeable_concept(
            SystemConstants.OBSERVATION_CATEGORY_SYSTEM,
            incoming_data.observationCategory,
            fhir_constants.ObservationResource.category_display.get(incoming_data.observationCategory)
        )
        if category:
            fhir_resource.category = [category]

    fhir_resource.effectiveDateTime = fhir_utils.get_datetime(incoming_data.observationDateTime, record.get('timeZone'))
    ext_id = fhir_utils.get_external_identifier(obs_code, "Observation", fhir_resource)
    if ext_id:
        identifiers.append(ext_id)

    if any([incoming_data.practitionerNPI, incoming_data.practitionerInternalId]):
        practitioner_resources = practitioner.convert_record(group_by_key, record, resource_meta)
        if practitioner_resources:
            performer = practitioner_resources[0]
            fhir_resource.performer = [fhir_utils.get_resource_reference(performer)]
        resources.extend(practitioner_resources)

    _set_observation_value(fhir_resource, incoming_data)
    _set_observation_reference_range(fhir_resource, incoming_data)
    _set_observation_interpretation(fhir_resource, incoming_data)

    resources.append(fhir_resource)
    return resources
