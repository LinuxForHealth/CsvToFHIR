# CSVToFHIR Internal Format

CSVToFHIR parses CSV records into a Pandas [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) using [tasks](../src/linuxforhealth/csvtofhir/pipeline/tasks.py) to standardize data into an internal representation.
This internal representation provides a single normalized format used to convert records to FHIR resources. The sections below lists the fields used for each internal CSV data model.

## Table of Contents
- [Allergy Intolerance](#allergy-intolerance)
- [Basic](#basic)
- [Condition](#condition)
- [Encounter](#encounter)
- [Immunization](#immunization)
- [Location](#location)
- [Medication Use](#medication-use)
- [Observation](#observation)
- [Patient](#patient)
- [Practitioner](#practitioner)
- [Procedure](#procedure)
- [Unstructured](#unstructured)

## Allergy Intolerance

See [AllergyIntoleranceCsv](/src/linuxforhealth/csvtofhir/model/csv/allergy_intolerance.py) for the AllergyIntolerance model fields.

The Allergy Intolerance conversion produces the following FHIR resources:

- AllergyIntolerance

## Condition

See [ConditionCsv](/src/linuxforhealth/csvtofhir/model/csv/condition.py) for the Condition model fields.

The Condition conversion produces the following FHIR resources:

- Condition
- Encounter (optional)

## Basic

See [BasicCsv](/src/linuxforhealth/csvtofhir/model/csv/basic.py) for the Condition model fields.

The Basic conversion produces the following FHIR resources:

- Basic

## Encounter

See [EncounterCsv](/src/linuxforhealth/csvtofhir/model/csv/encounter.py) for the Encounter model fields.

The Encounter conversion produces the following FHIR resources:

- Encounter
- Practitioner (Optional)
- PractitionerRole (Optional)
- Location (Optional)

## Immunization

See [ImmunizationCsv](/src/linuxforhealth/csvtofhir/model/csv/immunization.py) for the Immunization model fields.

The Condition conversion produces the following FHIR resources:

- Immunization
- Organization (optional)

## Location

See [LocationCsv](/src/linuxforhealth/csvtofhir/model/csv/location.py) for the Location model fields.

The Location conversion produces the following FHIR resources:

- Location


## Medication Use

See [MedicationUseCsv](/src/linuxforhealth/csvtofhir/model/csv/medication_use.py) for Medication model fields.

The Medication Use conversion produces the following FHIR resources:

- MedicationAdministration (Optional)
- MedicationRequest (Optional)
- MedicationStatement (Optional)
- Encounter (Optional)

## Observation

See [ObservationCsv](/src/linuxforhealth/csvtofhir/model/csv/observation.py) for the Observation model fields.

The Observation conversion produces the following FHIR resources:

- Patient
- Observation
- Practitioner (Optional)


## Patient

See [PatientCsv](/src/linuxforhealth/csvtofhir/model/csv/patient.py) for the Patient model fields.

The Patient conversion produces the following FHIR resources:

- Patient


## Practitioner

See [ParactitionerCsv](/src/linuxforhealth/csvtofhir/model/csv/practitioner.py) for the Practitioner model fields.

The Practitioner conversion produces the following FHIR resources:

- Practitioner (Optional)
- PractitionerRole (Optional)

## Procedure

See [ProcedureCsv](/src/linuxforhealth/csvtofhir/model/csv/procedure.py) for the Procedure model fields.

The Procedure conversion produces the following FHIR resources:

- Encounter (Optional)
- Practitioner (Optional)
- Procedure


## Unstructured

See [UnstructuredCsv](/src/linuxforhealth/csvtofhir/model/csv/unstructured.py) for the Unstructured model fields.

The Unstructured conversion produces the following FHIR resources:

- Attachment
- Practitioner
- DiagnosticReport (Optional)
- DocumentReference (Optional)
