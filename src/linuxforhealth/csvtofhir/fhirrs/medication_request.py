from typing import Dict, List, Union

from fhir.resources.encounter import Encounter
from fhir.resources.medicationrequest import MedicationRequest, MedicationRequestDispenseRequest
from fhir.resources.meta import Meta
from fhir.resources.quantity import Quantity
from fhir.resources.resource import Resource

from linuxforhealth.csvtofhir.fhirrs import encounter, medication_use
from linuxforhealth.csvtofhir.fhirutils import fhir_utils
from linuxforhealth.csvtofhir.model.csv.medication_use import RESOURCE_TYPE_MED_REQUEST, MedicationUseCsv
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def convert_record(
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> List[Resource]:
    record["resourceType"] = RESOURCE_TYPE_MED_REQUEST
    return medication_use.convert_record(group_by_key, record, resource_meta)


def create_encounter(
    incoming_data: MedicationUseCsv,
    group_by_key: str, record: Dict, resource_meta: Meta = None
) -> Union[Encounter, None]:
    '''
    Builds an Encounter if there is data to hold in it.
    '''
    if incoming_data.encounterClaimType is not None or incoming_data.encounterClassCode is not None:
        encounter_resources = encounter.convert_record(group_by_key, record, resource_meta)
        return encounter_resources[0]  # Will always just have a single Encounter
    return None


def construct_dispense(incoming_data: MedicationUseCsv, fhir_resource: MedicationRequest, record: Dict):
    '''
    Builds MedicationRequest.dispenseRequest, adds to the fhir_resource
    '''
    dispense = MedicationRequestDispenseRequest.construct()
    dispense.numberOfRepeatsAllowed = incoming_data.medicationRefills
    dispense.validityPeriod = fhir_utils.get_fhir_type_period(
        incoming_data.medicationValidityStart, incoming_data.medicationValidityEnd, record.get('timeZone'))
    if incoming_data.medicationQuantity:
        try:
            value_num = int(incoming_data.medicationQuantity)
            quantity = Quantity.construct(value=value_num)
            dispense.quantity = quantity
        except ValueError:
            logger.warning("medicationQuantity not a number")

    fhir_resource.dispenseRequest = dispense
