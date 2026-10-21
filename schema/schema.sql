-- =========================================================
-- MEDICINE DISPENSER SYSTEM
-- PostgreSQL Relational Schema (BCNF Compliant Batching)
-- =========================================================


-- =========================================================
-- 1. USER
-- =========================================================
CREATE TABLE "USER" (
    UserID BIGINT GENERATED ALWAYS AS IDENTITY,
    Username VARCHAR(100) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    MiddleName VARCHAR(50),
    LastName VARCHAR(50) NOT NULL,
    PhoneNumber VARCHAR(15),

    CONSTRAINT pk_user 
        PRIMARY KEY (UserID),

    CONSTRAINT uq_user_username 
        UNIQUE (Username),

    CONSTRAINT chk_user_role 
        CHECK (Role IN ('PATIENT', 'DOCTOR', 'CAREGIVER'))
);


-- =========================================================
-- 2. PATIENT
-- =========================================================
CREATE TABLE PATIENT (
    UserID BIGINT,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(20),
    Street VARCHAR(150),
    City VARCHAR(100),
    State VARCHAR(100),
    PostalCode VARCHAR(10),

    CONSTRAINT pk_patient 
        PRIMARY KEY (UserID),

    CONSTRAINT fk_patient_user 
        FOREIGN KEY (UserID) 
        REFERENCES "USER"(UserID) 
        ON DELETE CASCADE
);


-- =========================================================
-- 3. DOCTOR
-- =========================================================
CREATE TABLE DOCTOR (
    UserID BIGINT,
    MedicalRegistrationNumber VARCHAR(50) NOT NULL,
    Specialization VARCHAR(100) NOT NULL,

    CONSTRAINT pk_doctor 
        PRIMARY KEY (UserID),

    CONSTRAINT uq_doctor_registration 
        UNIQUE (MedicalRegistrationNumber),

    CONSTRAINT fk_doctor_user 
        FOREIGN KEY (UserID) 
        REFERENCES "USER"(UserID) 
        ON DELETE CASCADE
);


-- =========================================================
-- 4. CAREGIVER
-- =========================================================
CREATE TABLE CAREGIVER (
    UserID BIGINT,

    CONSTRAINT pk_caregiver 
        PRIMARY KEY (UserID),

    CONSTRAINT fk_caregiver_user 
        FOREIGN KEY (UserID) 
        REFERENCES "USER"(UserID) 
        ON DELETE CASCADE
);


-- =========================================================
-- 5. CAREGIVER - PATIENT RELATIONSHIP
-- =========================================================
CREATE TABLE CAREGIVER_PATIENT (
    CaregiverID BIGINT NOT NULL,
    PatientID BIGINT NOT NULL,
    RelationshipToPatient VARCHAR(100) NOT NULL,

    CONSTRAINT pk_caregiver_patient 
        PRIMARY KEY (CaregiverID, PatientID),

    CONSTRAINT fk_cp_caregiver 
        FOREIGN KEY (CaregiverID) 
        REFERENCES CAREGIVER(UserID) 
        ON DELETE CASCADE,

    CONSTRAINT fk_cp_patient 
        FOREIGN KEY (PatientID) 
        REFERENCES PATIENT(UserID) 
        ON DELETE CASCADE
);


-- =========================================================
-- 6. MEDICINE
-- =========================================================
CREATE TABLE MEDICINE (
    MedicineID BIGINT GENERATED ALWAYS AS IDENTITY,
    MedicineName VARCHAR(150) NOT NULL,
    Strength VARCHAR(50) NOT NULL,
    DosageForm VARCHAR(50) NOT NULL,
    Manufacturer VARCHAR(150),

    CONSTRAINT pk_medicine 
        PRIMARY KEY (MedicineID)
);


-- =========================================================
-- 7. PRESCRIPTION
-- =========================================================
CREATE TABLE PRESCRIPTION (
    PrescriptionID BIGINT GENERATED ALWAYS AS IDENTITY,
    PatientID BIGINT NOT NULL,
    DoctorID BIGINT NOT NULL,
    PrescriptionDate DATE NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,

    CONSTRAINT pk_prescription 
        PRIMARY KEY (PrescriptionID),

    CONSTRAINT fk_prescription_patient 
        FOREIGN KEY (PatientID) 
        REFERENCES PATIENT(UserID),

    CONSTRAINT fk_prescription_doctor 
        FOREIGN KEY (DoctorID) 
        REFERENCES DOCTOR(UserID),

    CONSTRAINT chk_prescription_dates 
        CHECK (EndDate >= StartDate)
);


-- =========================================================
-- 8. PRESCRIPTION ITEM
-- =========================================================
CREATE TABLE PRESCRIPTION_ITEM (
    PrescriptionItemID BIGINT GENERATED ALWAYS AS IDENTITY,
    PrescriptionID BIGINT NOT NULL,
    MedicineID BIGINT NOT NULL,
    Dosage VARCHAR(100) NOT NULL,
    Frequency VARCHAR(100) NOT NULL,
    Duration VARCHAR(100) NOT NULL,

    CONSTRAINT pk_prescription_item 
        PRIMARY KEY (PrescriptionItemID),

    CONSTRAINT fk_pi_prescription 
        FOREIGN KEY (PrescriptionID) 
        REFERENCES PRESCRIPTION(PrescriptionID) 
        ON DELETE CASCADE,

    CONSTRAINT fk_pi_medicine 
        FOREIGN KEY (MedicineID) 
        REFERENCES MEDICINE(MedicineID)
);


-- =========================================================
-- 9. MEDICINE BATCH (BCNF Implementation)
-- =========================================================
CREATE TABLE MEDICINE_BATCH (
    BatchNumber VARCHAR(100) NOT NULL,
    MedicineID BIGINT NOT NULL,
    ExpiryDate DATE NOT NULL,

    CONSTRAINT pk_medicine_batch 
        PRIMARY KEY (MedicineID, BatchNumber),

    CONSTRAINT fk_batch_medicine 
        FOREIGN KEY (MedicineID) 
        REFERENCES MEDICINE(MedicineID) 
        ON DELETE CASCADE
);


-- =========================================================
-- 10. INVENTORY
-- =========================================================
CREATE TABLE INVENTORY (
    InventoryID BIGINT GENERATED ALWAYS AS IDENTITY,
    MedicineID BIGINT NOT NULL,
    BatchNumber VARCHAR(100) NOT NULL,
    QuantityAvailable INTEGER NOT NULL,
    MinimumStockLevel INTEGER NOT NULL,

    CONSTRAINT pk_inventory 
        PRIMARY KEY (InventoryID),

    CONSTRAINT fk_inventory_batch 
        FOREIGN KEY (MedicineID, BatchNumber) 
        REFERENCES MEDICINE_BATCH(MedicineID, BatchNumber) 
        ON DELETE RESTRICT,

    CONSTRAINT chk_inventory_quantity 
        CHECK (QuantityAvailable >= 0),

    CONSTRAINT chk_inventory_minimum 
        CHECK (MinimumStockLevel >= 0)
);


-- =========================================================
-- 11. DISPENSER SLOT
-- =========================================================
CREATE TABLE DISPENSER_SLOT (
    SlotID BIGINT GENERATED ALWAYS AS IDENTITY,
    SlotNumber INTEGER NOT NULL,
    Capacity INTEGER NOT NULL,

    CONSTRAINT pk_dispenser_slot 
        PRIMARY KEY (SlotID),

    CONSTRAINT uq_slot_number 
        UNIQUE (SlotNumber),

    CONSTRAINT chk_slot_capacity 
        CHECK (Capacity > 0)
);


-- =========================================================
-- 12. INVENTORY - SLOT
-- =========================================================
CREATE TABLE INVENTORY_SLOT (
    InventoryID BIGINT NOT NULL,
    SlotID BIGINT NOT NULL,

    CONSTRAINT pk_inventory_slot 
        PRIMARY KEY (InventoryID),

    CONSTRAINT uq_inventory_slot 
        UNIQUE (SlotID),

    CONSTRAINT fk_is_inventory 
        FOREIGN KEY (InventoryID) 
        REFERENCES INVENTORY(InventoryID) 
        ON DELETE CASCADE,

    CONSTRAINT fk_is_slot 
        FOREIGN KEY (SlotID) 
        REFERENCES DISPENSER_SLOT(SlotID) 
        ON DELETE RESTRICT
);


-- =========================================================
-- 13. DISPENSE SCHEDULE
-- =========================================================
CREATE TABLE DISPENSE_SCHEDULE (
    ScheduleID BIGINT GENERATED ALWAYS AS IDENTITY,
    PrescriptionItemID BIGINT NOT NULL,
    ScheduledTime TIME NOT NULL,
    QuantityToDispense INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,

    CONSTRAINT pk_dispense_schedule 
        PRIMARY KEY (ScheduleID),

    CONSTRAINT fk_schedule_prescription_item 
        FOREIGN KEY (PrescriptionItemID) 
        REFERENCES PRESCRIPTION_ITEM(PrescriptionItemID) 
        ON DELETE CASCADE,

    CONSTRAINT chk_schedule_quantity 
        CHECK (QuantityToDispense > 0),

    CONSTRAINT chk_schedule_dates 
        CHECK (EndDate >= StartDate)
);


-- =========================================================
-- 14. DISPENSE LOG
-- =========================================================
CREATE TABLE DISPENSE_LOG (
    DispenseID BIGINT GENERATED ALWAYS AS IDENTITY,
    ScheduleID BIGINT NOT NULL,
    DispenseDateTime TIMESTAMPTZ NOT NULL,
    QuantityDispensed INTEGER NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FailureReason TEXT,

    CONSTRAINT pk_dispense_log 
        PRIMARY KEY (DispenseID),

    CONSTRAINT fk_log_schedule 
        FOREIGN KEY (ScheduleID) 
        REFERENCES DISPENSE_SCHEDULE(ScheduleID) 
        ON DELETE CASCADE,

    CONSTRAINT chk_dispense_quantity 
        CHECK (QuantityDispensed >= 0),

    CONSTRAINT chk_dispense_status 
        CHECK (Status IN ('SUCCESS', 'FAILED', 'PARTIAL'))
);

-- =========================================================
-- 15. NFC CARD
-- =========================================================
CREATE TABLE NFC_CARD (
    CardID BIGINT GENERATED ALWAYS AS IDENTITY,
    UserID BIGINT NOT NULL,
    NfcUid VARCHAR(255) NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    AssignedAt TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_nfc_card 
        PRIMARY KEY (CardID),
        
    CONSTRAINT uq_nfc_uid 
        UNIQUE (NfcUid),

    CONSTRAINT fk_nfc_user 
        FOREIGN KEY (UserID) 
        REFERENCES "USER"(UserID) 
        ON DELETE CASCADE
);
