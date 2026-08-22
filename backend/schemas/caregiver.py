from pydantic import BaseModel, Field

class CaregiverBase(BaseModel):
    pass

class CaregiverOut(BaseModel):
    userid: int
    
    class Config:
        from_attributes = True

class CaregiverPatientBase(BaseModel):
    caregiver_id: int
    patient_id: int
    relationship_to_patient: str = Field(..., max_length=100)

class CaregiverPatientCreate(CaregiverPatientBase):
    pass

class CaregiverPatientOut(CaregiverPatientBase):
    class Config:
        from_attributes = True
