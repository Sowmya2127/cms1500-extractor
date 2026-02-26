from pydantic import BaseModel, field_validator
from typing import Optional, List, Any


class ServiceLine(BaseModel):
    date_of_service_from: Optional[str] = None
    date_of_service_to: Optional[str] = None
    place_of_service: Optional[str] = None
    emg: Optional[str] = None
    procedure_code: Optional[str] = None
    modifier: Optional[str] = None
    diagnosis_pointer: Optional[str] = None
    charges: Optional[float] = None
    days_or_units: Optional[int] = None
    epsdt_family_plan: Optional[str] = None
    rendering_provider_id: Optional[str] = None
    rendering_provider_npi: Optional[str] = None


class CMS1500(BaseModel):
    # ── PRIORITY FIELDS ──────────────────────────────────────────────────────
    patient_name: Optional[str] = None
    member_id: Optional[str] = None
    provider_name: Optional[str] = None
    date_of_service: Optional[List[str]] = None
    diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    total_charge: Optional[float] = None

    # ── ALL OTHER FIELDS ─────────────────────────────────────────────────────
    insurance_type: Optional[str] = None
    insured_id_number: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_sex: Optional[str] = None
    insured_name: Optional[str] = None
    patient_address: Optional[str] = None
    patient_city: Optional[str] = None
    patient_state: Optional[str] = None
    patient_zip: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_relationship_to_insured: Optional[str] = None
    insured_address: Optional[str] = None
    insured_city: Optional[str] = None
    insured_state: Optional[str] = None
    insured_zip: Optional[str] = None
    insured_phone: Optional[str] = None
    reserved_for_nucc_use: Optional[str] = None
    other_insured_name: Optional[str] = None
    other_insured_policy_or_group_number: Optional[str] = None
    other_insurance_plan_name: Optional[str] = None
    condition_related_to_employment: Optional[str] = None
    condition_related_to_auto_accident: Optional[str] = None
    auto_accident_state: Optional[str] = None
    condition_related_to_other_accident: Optional[str] = None
    claim_codes: Optional[str] = None
    insured_policy_group_or_feca_number: Optional[str] = None
    insured_dob: Optional[str] = None
    insured_sex: Optional[str] = None
    other_claim_id: Optional[str] = None
    insurance_plan_name: Optional[str] = None
    another_health_benefit_plan: Optional[str] = None
    patient_signature: Optional[str] = None
    patient_signature_date: Optional[str] = None
    insured_signature: Optional[str] = None
    illness_injury_pregnancy_date: Optional[str] = None
    date_qualifier: Optional[str] = None
    other_date: Optional[str] = None
    other_date_qualifier: Optional[str] = None
    unable_to_work_from_date: Optional[str] = None
    unable_to_work_to_date: Optional[str] = None
    referring_provider_name: Optional[str] = None
    referring_provider_qualifier: Optional[str] = None
    other_id_number: Optional[str] = None
    referring_provider_npi: Optional[str] = None
    hospitalization_from_date: Optional[str] = None
    hospitalization_to_date: Optional[str] = None
    additional_claim_information: Optional[str] = None
    outside_lab: Optional[str] = None
    outside_lab_charges: Optional[float] = None
    icd_indicator: Optional[str] = None
    resubmission_code: Optional[str] = None
    original_ref_number: Optional[str] = None
    prior_authorization_number: Optional[str] = None
    service_lines: Optional[List[ServiceLine]] = None
    federal_tax_id: Optional[str] = None
    tax_id_type: Optional[str] = None
    patient_account_number: Optional[str] = None
    accept_assignment: Optional[str] = None
    amount_paid: Optional[float] = None
    reserved_for_nucc_use_30: Optional[str] = None
    signature_of_physician: Optional[str] = None
    signature_date: Optional[str] = None
    service_facility_name: Optional[str] = None
    service_facility_address: Optional[str] = None
    service_facility_city_state_zip: Optional[str] = None
    service_facility_npi: Optional[str] = None
    service_facility_other_id: Optional[str] = None
    billing_provider_phone: Optional[str] = None
    billing_provider_name: Optional[str] = None
    billing_provider_address: Optional[str] = None
    billing_provider_city_state_zip: Optional[str] = None
    billing_provider_npi: Optional[str] = None
    billing_provider_other_id: Optional[str] = None
    
    @field_validator("total_charge", "amount_paid", "outside_lab_charges", mode="before")
    @classmethod
    def coerce_float(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        try:
            return float(str(v).replace(",", "").replace("$", "").strip())
        except (ValueError, TypeError):
            return None

    @field_validator("accept_assignment", mode="before")
    @classmethod
    def coerce_str(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, bool):
            return "yes" if v else "no" 
        return str(v)


def validate(data: dict) -> CMS1500:
    if not data.get("member_id"):
        data["member_id"] = data.get("insured_id_number")
    if not data.get("provider_name"):
        data["provider_name"] = data.get("billing_provider_name") or data.get("signature_of_physician")
    if not data.get("procedure_codes"):
        lines = data.get("service_lines") or []
        codes = [ln.get("procedure_code") for ln in lines if isinstance(ln, dict) and ln.get("procedure_code")]
        data["procedure_codes"] = codes if codes else None
    if not data.get("date_of_service"):
        lines = data.get("service_lines") or []
        dates = list({ln.get("date_of_service_from") for ln in lines if isinstance(ln, dict) and ln.get("date_of_service_from")})
        data["date_of_service"] = dates if dates else None
    return CMS1500(**data)