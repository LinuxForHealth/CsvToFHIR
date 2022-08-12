from linuxforhealth.csvtofhir.fhirrs.allergy_intolerance import \
    convert_record as convert_allergy_intolerance
from linuxforhealth.csvtofhir.fhirrs.condition import convert_record as convert_condition
from linuxforhealth.csvtofhir.fhirrs.diagnostic_report import \
    convert_record as convert_diagnostic_report
from linuxforhealth.csvtofhir.fhirrs.document_reference import \
    convert_record as convert_document_reference
from linuxforhealth.csvtofhir.fhirrs.encounter import convert_record as convert_encounter
from linuxforhealth.csvtofhir.fhirrs.immunization import convert_record as convert_immunization
from linuxforhealth.csvtofhir.fhirrs.location import convert_record as convert_location
from linuxforhealth.csvtofhir.fhirrs.medication_administration import \
    convert_record as convert_medication_administration
from linuxforhealth.csvtofhir.fhirrs.medication_request import \
    convert_record as convert_medication_request
from linuxforhealth.csvtofhir.fhirrs.medication_statement import \
    convert_record as convert_medication_statement
from linuxforhealth.csvtofhir.fhirrs.medication_use import \
    convert_record as convert_medication_use
from linuxforhealth.csvtofhir.fhirrs.observation import convert_record as convert_observation
from linuxforhealth.csvtofhir.fhirrs.patient import convert_record as convert_patient
from linuxforhealth.csvtofhir.fhirrs.practitioner import convert_record as convert_practitioner
from linuxforhealth.csvtofhir.fhirrs.procedure import convert_record as convert_procedure
from linuxforhealth.csvtofhir.fhirrs.unstructured import convert_record as convert_unstructured

conversion_by_resource = {
    "AllergyIntolerance": convert_allergy_intolerance,
    "Condition": convert_condition,
    "DiagnosticReport": convert_diagnostic_report,
    "DocumentReference": convert_document_reference,
    "Encounter": convert_encounter,
    "Immunization": convert_immunization,
    "Location": convert_location,
    "MedicationAdministration": convert_medication_administration,
    "MedicationRequest": convert_medication_request,
    "MedicationStatement": convert_medication_statement,
    "MedicationUse": convert_medication_use,
    "Observation": convert_observation,
    "Patient": convert_patient,
    "Practitioner": convert_practitioner,
    "Procedure": convert_procedure,
    "Unstructured": convert_unstructured
}
