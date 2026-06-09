from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import date, datetime

class ClinicalDataBase(BaseModel):
    # PAGE 1: Case Overview
    patient_first_name: Optional[str] = None
    patient_last_name: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_dob: Optional[date] = None
    patient_address: Optional[str] = None
    medical_history: Optional[bool] = False
    medications: Optional[bool] = False
    allergies: Optional[bool] = False
    immunizations: Optional[bool] = False
    past_medical_history: Optional[bool] = False
    family_history: Optional[bool] = False
    current_drug_regimens: Optional[str] = None
    current_medications: Optional[str] = None
    current_allergies: Optional[str] = None
    current_immunizations: Optional[str] = None
    
    # PAGE 2: Presenting Complaints
    complaints_description: Optional[str] = None
    complaints_history: Optional[str] = None
    history_of_presenting_complaints: Optional[str] = None
    
    # PAGE 3: Allergies & Family History
    allergy_years: Optional[str] = None
    allergy_treatment: Optional[str] = None
    allergy_product_used: Optional[str] = None
    allergy_current: Optional[bool] = False
    allergy_reason: Optional[str] = None
    family_birthdate: Optional[date] = None
    family_mother: Optional[str] = None
    family_father: Optional[str] = None
    family_mother_male: Optional[str] = None
    family_male_other: Optional[str] = None
    family_sex_of: Optional[str] = None
    family_sex_of_2: Optional[str] = None
    
    # PAGE 4: Aggravation & Amelioration + Mental Trail
    emotional_family: Optional[str] = None
    emotional_authority: Optional[str] = None
    physical_leadership: Optional[str] = None
    physical_setting: Optional[str] = None
    motivational_upbringing: Optional[str] = None
    motivational_acquiring_1: Optional[str] = None
    motivational_acquiring_2: Optional[str] = None
    future_responsibility: Optional[str] = None
    future_meaning: Optional[str] = None
    future_decision: Optional[str] = None
    future_creation: Optional[str] = None
    future_order: Optional[str] = None
    future_stress: Optional[str] = None
    future_time: Optional[str] = None
    future_create: Optional[str] = None
    future_destiny: Optional[str] = None
    positive_reinforcement: Optional[str] = None
    motivation: Optional[str] = None
    stress_on_task_performance: Optional[str] = None
    time_management: Optional[str] = None
    success_and_promotion: Optional[str] = None
    job_name_1: Optional[str] = None
    job_name_2: Optional[str] = None
    job_position_1: Optional[str] = None
    job_position_2: Optional[str] = None
    job_position_3: Optional[str] = None
    job_position_4: Optional[str] = None
    activity_name: Optional[str] = None
    activity_position: Optional[str] = None
    ev_event: Optional[str] = None
    ev_time: Optional[str] = None
    ev_position_1: Optional[str] = None
    ev_position_2: Optional[str] = None
    ev_position_3: Optional[str] = None
    ev_position_4: Optional[str] = None
    
    # PAGE 5: Personal History
    personal_history_details: Optional[str] = None
    identified_causations: Optional[str] = None
    disease_name: Optional[str] = None
    treatment_history: Optional[str] = None
    treatment_method: Optional[str] = None
    treatment_result: Optional[str] = None
    result: Optional[str] = None
    sides_parietal: Optional[str] = None
    vertex: Optional[str] = None
    sensation: Optional[str] = None
    sleep_pattern: Optional[str] = None
    bathing: Optional[str] = None
    head_injury: Optional[str] = None
    head_skin: Optional[str] = None
    concomitants: Optional[str] = None
    modality: Optional[str] = None
    forehead: Optional[str] = None
    perspiration: Optional[str] = None
    alcoholic: Optional[str] = None
    movement: Optional[str] = None
    endocrin: Optional[str] = None
    temple: Optional[str] = None
    vertigo: Optional[str] = None
    time_of_vertigo: Optional[str] = None
    vomiting: Optional[str] = None
    dropsical: Optional[str] = None
    
    # PAGE 6: Obstetrical & General Clinical
    cycle_regularity: Optional[str] = None
    cycle_days: Optional[int] = 28
    duration_days: Optional[int] = 5
    flow: Optional[str] = None
    general_serial_history: Optional[str] = None
    marriage_notes: Optional[str] = None
    pregnancy_notes: Optional[str] = None
    gravida: Optional[int] = None
    para: Optional[int] = None
    abortions: Optional[int] = None
    obstetrical_complications: Optional[str] = None
    maternal_history: Optional[str] = None
    paternal_history: Optional[str] = None
    sisters_history: Optional[str] = None
    brothers_history: Optional[str] = None
    mothers_on: Optional[str] = None
    husbands_partner: Optional[str] = None
    excreta_quantity: Optional[str] = None
    excreta_colour: Optional[str] = None
    excreta_consumption: Optional[str] = None
    excreta_cloths: Optional[str] = None
    excreta_odor: Optional[str] = None
    excreta_stain: Optional[str] = None
    excreta_pain: Optional[str] = None
    fever: Optional[str] = None
    chill: Optional[str] = None
    sweat: Optional[str] = None
    time_onset: Optional[str] = None
    befores: Optional[str] = None
    duration: Optional[str] = None
    past_history: Optional[str] = None
    personality_type: Optional[str] = None
    concomitant: Optional[str] = None
    drugs: Optional[str] = None
    
    # PAGE 7: Social, Psychological & Mental
    aunt: Optional[str] = None
    uncle: Optional[str] = None
    daughter: Optional[str] = None
    wife: Optional[str] = None
    son: Optional[str] = None
    living_status: Optional[str] = None
    deceased: Optional[str] = None
    tea: Optional[str] = None
    coffee: Optional[str] = None
    alcohol: Optional[str] = None
    beer: Optional[str] = None
    tobacco: Optional[str] = None
    chewing: Optional[str] = None
    parental_attitude: Optional[str] = None
    society: Optional[str] = None
    work_place: Optional[str] = None
    family_dynamic: Optional[str] = None
    dissatisfaction: Optional[str] = None
    strain: Optional[str] = None
    love: Optional[str] = None
    hate: Optional[str] = None
    attachment: Optional[str] = None
    anger: Optional[str] = None
    sadness: Optional[str] = None
    anxiety: Optional[str] = None
    ego: Optional[str] = None
    jealous: Optional[str] = None
    suspicious: Optional[str] = None
    envy: Optional[str] = None
    memory_state: Optional[str] = None
    mental_characteristics: Optional[str] = None
    activity_levels: Optional[str] = None
    general_behavior: Optional[str] = None


class ClinicalDataCreate(ClinicalDataBase):
    centre_code: str
    hospital_no: str


class ClinicalDataUpdate(ClinicalDataBase):
    pass


class ClinicalDataResponse(ClinicalDataBase):
    id: str
    centre_code: str
    hospital_no: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
