# CSVToFHIR Internal Format

CSVToFHIR parses CSV records into a Pandas [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) using [tasks](../src/linuxforhealth/csvtofhir/pipeline/tasks.py) to standardize data into an internal representation.
This internal representation provides a single normalized format used to convert records to FHIR resources. The sections below lists the fields used for each internal CSV data model.

## Table of Contents
- [Allergy Intolerance](#allergy-intolerance)
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
The Allergy Intolerance Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- encounterInternalId
- encounterNumber
- resourceInternalId
- assigningAuthority
- allergySourceRecordId
- allergyCategory
- allergyType
- allergyRecordedDateTime
- allergyCode
- allergySystem
- allergyCodeText
- allergyCriticality
- allergyManifestationCode
- allergyManifestationSystem
- allergyManifestationText
- allergyManifestationCodeList
- allergyClinicalStatusCode
- allergyVerificationStatusCode
- allergyOnsetStartDateTime
- allergyOnsetEndDateTime

The Allergy Intolerance conversion produces the following FHIR resources:

- AllergyIntolerance


## Condition

See [ConditionCsv](/src/linuxforhealth/csvtofhir/model/csv/condition.py) for the Condition model fields.
The Condition Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- encounterInternalId
- encounterNumber
- encounterClaimType
- resourceInternalId
- assigningAuthority
- conditionSourceRecordId
- conditionCategory
- conditionClinicalStatus
- conditionVerificationStatus
- conditionDiagnosisRank
- conditionDiagnosisUse

- conditionRecordedDateTime
- conditionOnsetDateTime
- conditionAbatementDateTime
- conditionCode
- conditionCodeSystem
- conditionCodeText
- conditionSeverityCode
- conditionSeveritySystem
- conditionSeverityText
- conditionChronicity

The Condition conversion produces the following FHIR resources:

- Condition
- Encounter (optional)


## Encounter

See [EncounterCsv](/src/linuxforhealth/csvtofhir/model/csv/encounter.py) for the Encounter model fields.
The Encounter Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- encounterNumber
- resourceInternalId
- assigningAuthority
- encounterSourceRecordId
- encounterStatus
- encounterClassCode
- encounterClassText
- encounterClassSystem
- encounterPriorityCode
- encounterPriorityText
- encounterPriorityCodeSystem
- encounterStartDateTime
- encounterEndDateTime
- encounterLengthValue
- encounterLengthUnits
- encounterReasonCode
- encounterReasonCodeSystem
- encounterReasonCodeText
- hospitalizationAdmitSourceCode
- hospitalizationAdmitSourceCodeText
- hospitalizationAdmitSourceCodeSystem
- hospitalizationReAdmissionCode
- hospitalizationReAdmissionCodeText
- hospitalizationReAdmissionCodeSystem
- hospitalizationDischargeDispositionCode
- hospitalizationDischargeDispositionCodeText
- hospitalizationDischargeDispositionCodeSystem
- encounterParticipantSequenceId
- encounterParticipantTypeCode
- encounterParticipantTypeText
- encounterParticipantTypeCodeSystem
- practitionerInternalId
- practitionerNPI
- practitionerNameLast
- practitionerNameFirst
- practitionerGender
- practitionerRoleText
- practitionerRoleCodes
- practitionerRoleCodesSystem
- practitionerSpecialtyCodes
- practitionerSpecialtyCodesSystem
- practitionerSpecialtyText
- encounterLocationSequenceId
- encounterLocationPeriodStart
- encounterLocationPeriodEnd
- locationResourceInternalId
- locationName
- locationTypeCode
- locationTypeText
- locationTypeCodeSystem
- encounterInsuredEntryId
- encounterInsuredRank
- encounterInsuredCategoryCode
- encounterInsuredCategorySystem
- encounterInsuredCategoryText
- encounterDrgCode

The Encounter conversion produces the following FHIR resources:

- Encounter
- Practitioner (Optional)
- PractitionerRole (Optional)
- Location (Optional)

## Immunization

See [ImmunizationCsv](/src/linuxforhealth/csvtofhir/model/csv/immunization.py) for the Immunization model fields.
The Immunization Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- resourceInternalId
- immunizationSourceRecordId
- immunizationStatus
- immunizationDoseQuantity
- immunizationDoseUnit
- immunizationDoseText
- encounterNumber
- organizationResourceInternalId
- organizationName
- immunizationRouteCode
- immunizationRouteSystem
- immunizationRouteText
- immunizationSiteCode
- immunizationSiteSystem
- immunizationSiteText
- immunizationStatus
- immunizationStatusReasonCode
- immunizationStatusReasonSystem
- immunizationStatusReasonText
- immunizationVaccineCode
- immunizationVaccineText
- immunizationDate
- immunizationExpirationDate

The Condition conversion produces the following FHIR resources:

- Immunization
- Organization (optional)

## Location

See [LocationCsv](/src/linuxforhealth/csvtofhir/model/csv/location.py) for the Location model fields.

The Location Dictionary Record contains the following fields:

- assigningAuthority
- resourceInternalId
- locationName
- locationTypeCode
- locationTypeText
- locationTypeCodeSystem

The Location conversion produces the following FHIR resources:

- Location


## Medication Use

See [MedicationUseCsv](/src/linuxforhealth/csvtofhir/model/csv/medication_use.py) for Medication model fields.

The Medication Use Dictionary Record contains the following fields:

- resourceType
- patientInternalId
- accountNumber
- ssn
- mrn
- encounterInternalId
- encounterNumber
- encounterClaimType
- resourceInternalId
- medicationSourceRecordId
- medicationRxNumber
- assigningAuthority
- medicationUseStatus
- medicationUseCategoryCode
- medicationUseCategoryCodeSystem
- medicationUseCategoryCodeText
- medicationUseOccuranceDateTime
- medicationCode
- medicationCodeDisplay
- medicationCodeSystem
- medicationCodeText
- medicationCodeList
- medicationUseRouteCode
- medicationUseRouteCodeSystem
- medicationUseRouteText
- medicationUseDosageText
- medicationUseDosageValue
- medicationUseDosageUnit
- medicationValidityStart
- medicationValidityEnd
- medicationRefills
- medicationQuantity
- medicationAuthoredOn
- medicationRequestIntent

The Medication Use conversion produces the following FHIR resources:

- MedicationAdministration (Optional)
- MedicationRequest (Optional)
- MedicationStatement (Optional)
- Encounter (Optional)

## Observation

See [ObservationCsv](/src/linuxforhealth/csvtofhir/model/csv/observation.py) for the Observation model fields.
The HDP Observation Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- encounterNumber
- encounterInternalId
- resourceInternalId
- observationSourceRecordId
- assigningAuthority
- observationStatus
- observationCategory
- observationDateTime
- practitionerNPI
- practitionerInternalId
- observationCode
- observationCodeSystem
- observationCodeText
- observationCodeList
- observationValue
- observationValueUnits
- observationValueDataType
- observationRefRange
- observationRefRangeLow
- observationRefRangeHigh
- observationRefRangeText
- practitionerNameLast
- practitionerNameFirst
- practitionerGender
- practitionerRoleText
- practitionerRoleCode
- practitionerRoleCodesSystem
- practitionerSpecialtyCode
- practitionerSpecialtyCodesSystem
- practitionerSpecialtyText
- observationInterpretationCode
- observationInterpretationCodeSystem
- observationInterpretationCodeText
- noteText

The Observation conversion produces the following FHIR resources:

- Patient
- Observation
- Practitioner (Optional)


## Patient

See [PatientCsv](/src/linuxforhealth/csvtofhir/model/csv/patient.py) for the Patient model fields.
The Patient Dictionary Record contains the following fields:

- patientInternalId
- patientSourceRecordId
- accountNumber
- ssn
- driversLicense
- driversLicenseSystem
- mrn
- assigningAuthority
- nameFirst
- nameFirstMiddle
- nameMiddle
- nameLast
- nameFirstMiddleLast
- prefix
- suffix
- birthDate
- deceasedDateTime
- deceasedBoolean
- multipleBirthBoolean
- multipleBirthInteger
- address1
- address2
- city
- state
- postalCode
- country
- addressText
- telecomPhone
- race
- raceSystem
- ethnicity
- ethnicitySystem
- gender
- ageInWeeksForAgeUnder2Years
- ageInMonthsForAgeUnder8Years

The Patient conversion produces the following FHIR resources:

- Patient


## Practitioner

See [ParactitionerCsv](/src/linuxforhealth/csvtofhir/model/csv/practitioner.py) for the Practitioner model fields.
The Practitioner Dictionary Record contains the following fields:

- assigningAuthority
- resourceInternalId
- identifier_practitionerNPI
- practitionerNameLast
- practitionerNameFirst
- practitionerGender
- practitionerRoleText
- practitionerRoleCode
- practitionerRoleCodeList
- practitionerRoleCodeSystem
- practitionerSpecialtyCode
- practitionerSpecialtyCodeList
- practitionerSpecialtyCodeSystem
- practitionerSpecialtyText

The Practitioner conversion produces the following FHIR resources:

- Practitioner (Optional)
- PractitionerRole (Optional)

## Procedure

See [ProcedureCsv](/src/linuxforhealth/csvtofhir/model/csv/procedure.py) for the Procedure model fields.
The Procedure Dictionary Record contains the following fields:

- patientInternalId
- accountNumber
- ssn
- mrn
- encounterInternalId
- encounterNumber
- resourceInternalId
- procedureSourceRecordId
- assigningAuthority
- procedureStatus
- procedurePerformedDateTime
- procedureCategory
- procedureCategorySystem
- procedureCategoryText
- procedureCode
- procedureCodeSystem
- procedureCodeText
- procedureCodeList
- procedureModifierList
- procedureModifierSystem
- procedureEncounterSequenceId
- practitionerInternalId
- practitionerNPI
- practitionerNameLast
- practitionerNameFirst
- practitionerGender
- practitionerRoleText
- practitionerRoleCode
- practitionerRoleCodeSystem
- practitionerSpecialtyCode
- practitionerSpecialtyCodeSystem
- practitionerSpecialtyText

The Procedure conversion produces the following FHIR resources:

- Encounter (Optional)
- Practitioner (Optional)
- Procedure


## Unstructured

See [UnstructuredCsv](/src/linuxforhealth/csvtofhir/model/csv/unstructured.py) for the Unstructured model fields.
The Unstructured Dictionary Record contains the following fields:

- resourceType
- patientInternalId
- accountNumber
- ssn
- mrn
- accountNumber
- resourceInternalId
- encounterInternalId
- assigningAuthority
- resourceStatus
- documentStatus
- documentTypeCode
- documentTypeCodeSystem
- documentTypeCodeText
- documentDateTime
- documentAttachmentContentType
- documentAttachmentContent
- documentAttachmentTitle
- practitionerInternalId
- practitionerNPI
- practitionerNameLast
- practitionerNameFirst

The Unstructured conversion produces the following FHIR resources:

- Attachment
- Practitioner
- DiagnosticReport (Optional)
- DocumentReference (Optional)
