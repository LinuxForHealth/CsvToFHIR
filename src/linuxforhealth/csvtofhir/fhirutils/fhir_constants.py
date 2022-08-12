class ExtensionUrl:
    HL7_BASE_EXTENSION_URL = "http://hl7.org/fhir/StructureDefinition/"
    CDM_BASE_EXTENSION_URL = "http://ibm.com/fhir/cdm/StructureDefinition/"

    RACE_EXTENSION_SYSTEM = CDM_BASE_EXTENSION_URL + "local-race-cd"
    ETHNICITY_EXTENSION_SYSTEM = CDM_BASE_EXTENSION_URL + "ethnicity"
    CHRONICITY_EXTENSION_SYSTEM = HL7_BASE_EXTENSION_URL + "condition-diseaseCourse"
    DATA_ABSENT_EXTENSION_URL = HL7_BASE_EXTENSION_URL + "data-absent-reason"
    ENCOUNTER_DIAGNOSIS_USE_EXTENSION_URL = "http://ibm.com/fhir/cdm/CodeSystem/wh-diagnosis-use-type"
    ENCOUNTER_INSURED_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "insured"
    ENCOUNTER_INSURED_RANK_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "insured-rank"
    ENCOUNTER_INSURED_CATEGORY_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "insured-category"
    ENCOUNTER_CLAIM_TYPE_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "claim-type"
    META_TENANT_ID_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "tenant-id"
    META_SOURCE_FILE_ID_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "source-file-id"
    META_PROCESS_TIMESTAMP_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "process-timestamp"
    META_SOURCE_EVENT_TRIGGER_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "source-event-trigger"
    META_SOURCE_RECORD_TYPE_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "source-record-type"
    META_SOURCE_RECORD_ID_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "source-record-id"
    PATIENT_AGE_IN_MONTHS_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "snapshot-age-in-months"
    PATIENT_AGE_IN_WEEKS_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "snapshot-age-in-weeks"
    PROCEDURE_MODIFIER_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "procedure-modifier"
    PROCEDURE_SEQUENCE_EXTENSION_URL = CDM_BASE_EXTENSION_URL + "procedure-sequence"


class SystemConstants:
    # FHIR terminology systems
    ADMISSION_SOURCE_SYSTEM = "http://terminology.hl7.org/CodeSystem/admit-source"
    ALLERGY_CLINICAL_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"
    ALLERGY_VERIFICATION_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification"
    CLAIM_TYPE = "http://terminology.hl7.org/CodeSystem/claim-type"
    CMS_PLACE_OF_SERVICE_CODING_SYSTEM = "http://terminology.hl7.org/CodeSystem/ex-serviceplace"
    CONDITION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-category"
    CONDITION_CLINICAL_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-clinical"
    CONDITION_VERIFICATION_STATUS_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
    CONTACT_ENTITY_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/contactentity-type"
    COVERAGE_CLASS_SYSTEM = "http://terminology.hl7.org/CodeSystem/coverage-class"
    # FYI: Discharge Disposition HL7 standard uses numeric values "http://terminology.hl7.org/CodeSystem/v2-0112"
    DISCHARGE_DISPOSITION_SYSTEM = "http://terminology.hl7.org/CodeSystem/discharge-disposition"
    ENCOUNTER_CLASS_CODING_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    ETHNICITY_SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0189"
    INCIDENT_CODE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    LOCATION_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
    MED_ADM_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/medication-admin-category"
    MED_REQ_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/medicationrequest-category"
    MED_STM_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/medication-statement-category"
    OBSERVATION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/observation-category"
    OBSERVATION_INTERPRETATION_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
    ORGANIZATION_TYPE = "http://terminology.hl7.org/CodeSystem/organization-type"
    PARTICIPANT_TYPE_CODING_SYSTEM = "http://terminology.hl7.org/CodeSystem/participant-type"
    PARTICIPANT_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ParticipationType"
    PAYEE_TYPE_SYSTEM = "http://terminology.hl7.org/CodeSystem/payeetype"
    PRIORITY_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActPriority"
    PROCESS_PRIORITY = "http://terminology.hl7.org/CodeSystem/processpriority"
    PROVIDER_TAXONOMY_SYSTEM = "http://nucc.org/provider-taxonomy"
    RACE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-Race"
    RELATIONSHIP_CODING_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
    RE_ADMISSION_SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0092"

    # Misc systems
    DRG_CODE_SYSTEM = "https://www.cms.gov/icd10m/version37-fullcode-cms/fullcode_cms/P0002.html"

    # Medical coding systems
    CPT_SYSTEM = "http://www.ama-assn.org/go/cpt"
    CVX_SYSTEM = "http://hl7.org/fhir/sid/cvx"
    ICD9_SYSTEM = "http://hl7.org/fhir/sid/icd-9-cm"
    ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"
    ICD10PCS_SYSTEM = "http://terminology.hl7.org/CodeSystem/icd10PCS"
    LOINC_SYSTEM = "http://loinc.org"
    MESH_SYSTEM = "https://www.nlm.nih.gov/mesh"
    NCI_SYSTEM = "http://ncimeta.nci.nih.gov"
    NDC_SYSTEM = "http://hl7.org/fhir/sid/ndc"
    RXNORM_SYSTEM = "http://www.nlm.nih.gov/research/umls/rxnorm"
    SNOMED_SYSTEM = "http://snomed.info/sct"
    UMLS_SYSTEM = "http://terminology.hl7.org/CodeSystem/umls"
    # Medical coding system shortnames
    CVX = "CVX"
    CPT = "CPT"
    ICD10 = "ICD10"
    ICD10PCS = "ICD10PCS"
    ICD9 = "ICD9"
    LOINC = "LOINC"
    MESH = "MESH"
    NCI = "NCI"
    NDC = "NDC"
    RXNORM = "RXNORM"
    SNOMED = "SNOMED"
    UMLS = "UMLS"
    SystemURLsToCodeShortname: dict = {
        CPT_SYSTEM: CPT,
        CVX_SYSTEM: CVX,
        ICD10_SYSTEM: ICD10,
        ICD10PCS_SYSTEM: ICD10PCS,
        ICD9_SYSTEM: ICD9,
        LOINC_SYSTEM: LOINC,
        MESH_SYSTEM: MESH,
        NCI_SYSTEM: NCI,
        NDC_SYSTEM: NDC,
        RXNORM_SYSTEM: RXNORM,
        SNOMED_SYSTEM: SNOMED,
        UMLS_SYSTEM: UMLS
    }
    # Keys/values swapped from SystemURLsToCodeShortname
    CodingSystemURLs: dict = {value: key for key, value in SystemURLsToCodeShortname.items()}

    # Identifier systems
    NPI_SYSTEM_IDENTIFIER = "http://hl7.org.fhir/sid/us-npi"
    SS_CODING_SYSTEM = "http://hl7.org/fhir/sid/us-ssn"


class AllergyIntoleranceResource:
    """
    Defines display text for codes since we are not doing a system lookup
    """
    allergy_clinical_status_display = {  # https://www.hl7.org/fhir/valueset-allergyintolerance-clinical.html
        "active": "Active",
        "inactive": "Inactive",
        "resolved": "Resolved"
    }
    allergy_verification_status_display = {  # https://www.hl7.org/fhir/valueset-allergyintolerance-verification.html
        "unconfirmed": "Unconfirmed",
        "confirmed": "Confirmed",
        "refuted": "Refuted",
        "entered-in-error": "Entered in Error"
    }


class ConditionResource:
    category_display = {
        "problem-list-item": "Problem List Item",
        "encounter-diagnosis": "Encounter Diagnosis"
    }
    clinical_status_display = {
        "active": "Active",
        "recurrence": "Recurrence",
        "relapse": "Relapse",
        "inactive": "Inactive",
        "remission": "Remission",
        "resolved": "Resolved"
    }
    verification_status_display = {
        "unconfirmed": "Unconfirmed",
        "provisional": "Provisional",
        "differential": "Differential",
        "confirmed": "Confirmed",
        "refuted": "Refuted",
        "entered-in-error": "Entered in Error"
    }


class EncounterResource:
    """
    Defines display text used for the codes given we are not doing a system lookups.
    """
    class_display = {  # https://www.hl7.org/fhir/v3/ActEncounterCode/vs.html
        "IMP": "inpatient encounter",
        "EMER": "emergency",
        "AMB": "ambulatory",
        "RF": "Refill",
        "VR": "virtual",
        "HH": "home health"
    }
    participant_type_display = {  # https://www.hl7.org/fhir/valueset-encounter-participant-type.html
        "ADM": "admitter",
        "ATND": "attender",
        "CALLBCK": "callback contact",
        "CON": "consultant",
        "DIS": "discharger",
        "ESC": "escort",
        "REF": "referrer",
        "SPRF": "secondary performer",
        "PPRF": "primary performer",
        "PART": "Participation"
    }
    admit_source_display = {  # https://www.hl7.org/fhir/valueset-encounter-admit-source.html
        "hosp-trans": "Transferred from other hospital",
        "emd": "From accident/emergency department",
        "outp": "From outpatient department",
        "born": "Born in hospital",
        "gp": "General Practitioner referral",
        "mp": "Medical Practitioner/physician referral",
        "nursing": "From nursing home",
        "psych": "From psychiatric hospital",
        "rehab": "From rehabilitation facility",
        "other": "Other"
    }
    diagnosis_use_display = {  # http://terminology.hl7.org/CodeSystem/diagnosis-role plus more from CDM
        "AD": "Admission diagnosis",
        "CC": "Chief complaint",
        "principal-diagnosis": "Principal diagnosis"
    }


class ImmunizationResource:
    """
    Defines display text for immunization status codes since we are not doing a system lookup
    """
    immunization_status_reason_display = {  # https://build.fhir.org/valueset-immunization-status-reason.html
        "IMMUNE": "immunity",
        "MEDPREC": "medical precaution",
        "OSTOCK": "product out of stock",
        "PATOBJ": "patient objection",
        "PHILISOP": "philosophica objection",
        "RELIG": "religious objection",
        "VACEFF": "vaccine efficacy concerns",
        "VACSAF": "vaccine safety concerns"
    }


class LocationResource:
    type_display = {  # https://www.hl7.org/fhir/v3/ServiceDeliveryLocationRoleType/vs.html
        "ER": "Emergency room",
        "HOSP": "Hospital",
        "ICU": "Intensive care unit"
    }


class ObservationResource:
    """
    Defines display text for codes since we are not doing a system lookup
    """
    interpretation_code_display = {  # https://www.hl7.org/fhir/v3/ObservationInterpretation/cs.html
        "A": "Abnormal",
        "AA": "Critical abnormal",
        "H": "High",
        "L": "Low",
        "N": "Normal",
        "NEG": "Negative",
        "POS": "Positive"
    }

    category_display = {  # https://www.hl7.org/fhir/valueset-observation-category.html
        "social-history": "Social History",
        "vital-signs": "Vital Signs",
        "imaging": "Imaging",
        "laboratory": "Laboratory",
        "procedure": "Procedure",
        "survey": "Survey",
        "exam": "Exam",
        "therapy": "Therapy",
        "activity": "Activity"
    }


class PatientResource:
    """
    Defines display text for codes since we are not doing a system lookup
    """
    race_display = {  # https://www.hl7.org/fhir/v3/Race/cs.html
        "1002-5": "American Indian or Alaska Native",
        "1004-1": "American Indian",
        "2028-9": "Asian",
        "2029-7": "Asian Indian",
        "2030-5": "Bangladeshi",
        "2031-3": "Bhutanese",
        "2032-1": "Burmese",
        "2033-9": "Cambodian",
        "2034-7": "Chinese",
        "2035-4": "Taiwanese",
        "2036-2": "Filipino",
        "2037-0": "Hmong",
        "2038-8": "Indonesian",
        "2039-6": "Japanese",
        "2040-4": "Korean",
        "2041-2": "Laotian",
        "2042-0": "Malaysian",
        "2043-8": "Okinawan",
        "2044-6": "Pakistani",
        "2045-3": "Sri Lankan",
        "2046-1": "Thai",
        "2047-9": "Vietnamese",
        "2048-7": "Iwo Jiman",
        "2049-5": "Maldivian",
        "2050-3": "Nepalese",
        "2051-1": "Singaporean",
        "2052-9": "Madagascar",
        "2054-5": "Black or African American",
        "2056-0": "Black",
        "2058-6": "African American",
        "2060-2": "African",
        "2067-7": "Bahamian",
        "2068-5": "Barbadian",
        "2069-3": "Dominican",
        "2070-1": "Dominica Islander",
        "2071-9": "Haitian",
        "2072-7": "Jamaican",
        "2073-5": "Tobagoan",
        "2074-3": "Trinidadian",
        "2075-0": "West Indian",
        "2076-8": "Native Hawaiian or Other Pacific Islander",
        "2078-4": "Polynesian",
        "2500-7": "Other Pacific Islander",
        "2106-3": "White",
        "2108-9": "European",
        "2129-5": "Arab",
        "2131-1": "Other Race"
    }
    ethnicity_display = {
        "H": "Hispanic or Latino"
    }


class ValueDataAbsentReason:
    SYSTEM = "http://terminology.hl7.org/CodeSystem/data-absent-reason"
    CODE_TEMPORARILY_UNKNOWN = ("temp-unknown", "Temporarily Unknown")
    CODE_UNKNOWN = ("unknown", "Unknown")
