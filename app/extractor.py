import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

PRIORITY_FIELDS = """
PRIORITY FIELDS (extract these with highest accuracy):
  patient_name              - Box 2  (Last, First, Middle Initial)
  member_id                 - Box 1a (field displayed as Insured's id Number)
  provider_name             - Box 33 billing provider name, or Box 31 physician name
  date_of_service           - Box 24A dates of service (return as a list of strings)
  diagnosis_codes           - Box 21, labeled "DIAGNOSIS OR NATURE OF ILLNESS OR INJURY"
                              ICD codes appear in labeled slots A B C D E F G H I J K L
                              They look like: F50.2, F41.1, 389.10, 255.11, J06.9 etc.
                              Format: letters or numbers followed by numbers, often with a decimal point
                              IMPORTANT: Search the entire OCR text for any pattern matching
                              ICD code format (e.g. letter(s) + digits + optional .digits)
                              Return ALL found as a list. Do NOT confuse with procedure codes
  procedure_codes           - Box 24D CPT/HCPCS codes for each service line (return as a list)(procedure codes are purely numeric like 90837, 99213)
  total_charge              - Box 28 total charge amount (numeric)
"""

ALL_CMS_FIELDS = """
ALL FIELDS (extract everything, null if missing):
Box 1   - insurance_type
Box 1a  - insured_id_number
Box 2   - patient_name
Box 3   - patient_dob, patient_sex
Box 4   - insured_name
Box 5   - patient_address, patient_city, patient_state, patient_zip, patient_phone
Box 6   - patient_relationship_to_insured
Box 7   - insured_address, insured_city, insured_state, insured_zip, insured_phone
Box 9   - other_insured_name
Box 9a  - other_insured_policy_or_group_number
Box 9d  - other_insurance_plan_name
Box 10a - condition_related_to_employment
Box 10b - condition_related_to_auto_accident, auto_accident_state
Box 10c - condition_related_to_other_accident
Box 10d - claim_codes
Box 11  - insured_policy_group_or_feca_number
Box 11a - insured_dob, insured_sex
Box 11b - other_claim_id
Box 11c - insurance_plan_name
Box 11d - another_health_benefit_plan
Box 12  - patient_signature, patient_signature_date
Box 13  - insured_signature
Box 14  - illness_injury_pregnancy_date, date_qualifier
Box 15  - other_date, other_date_qualifier
Box 16  - unable_to_work_from_date, unable_to_work_to_date
Box 17  - referring_provider_name, referring_provider_qualifier
Box 17a - other_id_number
Box 17b - referring_provider_npi
Box 18  - hospitalization_from_date, hospitalization_to_date
Box 19  - additional_claim_information
Box 20  - outside_lab, outside_lab_charges
Box 21  - icd_indicator, diagnosis_codes (list)
Box 22  - resubmission_code, original_ref_number
Box 23  - prior_authorization_number
Box 24  - service_lines (list of objects: date_of_service_from, date_of_service_to,
           place_of_service, emg, procedure_code, modifier, diagnosis_pointer,
           charges, days_or_units, epsdt_family_plan, rendering_provider_id,
           rendering_provider_npi)
Box 25  - federal_tax_id, tax_id_type
Box 26  - patient_account_number
Box 27  - accept_assignment
Box 28  - total_charge (numeric)
Box 29  - amount_paid (numeric)
Box 31  - signature_of_physician, signature_date
Box 32  - service_facility_name, service_facility_address, service_facility_city_state_zip
Box 32a - service_facility_npi
Box 32b - service_facility_other_id
Box 33  - billing_provider_phone, billing_provider_name, billing_provider_address,
           billing_provider_city_state_zip
Box 33a - billing_provider_npi
Box 33b - billing_provider_other_id

Also include these top-level summary keys:
  member_id       -> same as insured_id_number
  provider_name   -> billing_provider_name (fall back to signature_of_physician)
  date_of_service -> list of unique service dates from Box 24A
  procedure_codes -> list of procedure_code values from all service_lines
  Diagnosis codes -> list of diagnosis_codes from Box 21 and all service_lines(A to L)
"""

def extract_fields(ocr_text: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a medical billing expert specializing in CMS-1500 health insurance claim forms.
Below is OCR text extracted from a CMS-1500 form.

Extract ALL fields and return ONLY a valid JSON object. Rules:
- Set missing or unreadable fields to null
- For lists (diagnosis_codes, procedure_codes, date_of_service, service_lines) always return a list even if only one item
- For numeric fields (total_charge, amount_paid, charges) return a number, not a string
- Do NOT include markdown, code fences, or any explanation — raw JSON only

{PRIORITY_FIELDS}

{ALL_CMS_FIELDS}

OCR Text:
{ocr_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip().rstrip("```")

    return json.loads(raw)