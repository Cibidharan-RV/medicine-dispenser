

BEGIN;

SELECT
    datname,
    pg_catalog.pg_get_userbyid(datdba) AS owner
FROM pg_database
WHERE datname = current_database();
-- =========================================================
-- 1. USER
-- =========================================================
INSERT INTO "USER" (UserID, Username, PasswordHash, Role, FirstName, MiddleName, LastName, PhoneNumber)
OVERRIDING SYSTEM VALUE VALUES 
(1, 'apatient1', 'hash1', 'PATIENT', 'Alan', 'J', 'Turing', '555-0101'),
(2, 'bpatient2', 'hash2', 'PATIENT', 'Barbara', 'L', 'Liskov', '555-0102'),
(3, 'cpatient3', 'hash3', 'PATIENT', 'Charles', NULL, 'Babbage', '555-0103'),
(4, 'dpatient4', 'hash4', 'PATIENT', 'Diana', 'M', 'Prince', '555-0104'),
(5, 'drsmith', 'hash5', 'DOCTOR', 'Alice', NULL, 'Smith', '555-0201'),
(6, 'drjones', 'hash6', 'DOCTOR', 'Bob', 'A', 'Jones', '555-0202'),
(7, 'drpatel', 'hash7', 'DOCTOR', 'Vikram', NULL, 'Patel', '555-0203'),
(8, 'care_elena', 'hash8', 'CAREGIVER', 'Elena', NULL, 'Gilbert', '555-0301'),
(9, 'care_frank', 'hash9', 'CAREGIVER', 'Frank', 'R', 'Castle', '555-0302'),
(10, 'care_grace', 'hash10', 'CAREGIVER', 'Grace', NULL, 'Hopper', '555-0303'),
(11, 'care_henry', 'hash11', 'CAREGIVER', 'Henry', NULL, 'McCoy', '555-0304');

-- =========================================================
-- 2. PATIENT
-- =========================================================
INSERT INTO PATIENT (UserID, DateOfBirth, Gender, Street, City, State, PostalCode)
VALUES 
(1, '1950-06-23', 'Male', '123 Math St', 'London', 'England', 'W1T 1JY'),
(2, '1939-11-07', 'Female', '456 Code Ave', 'Boston', 'MA', '02115'),
(3, '1960-12-26', 'Male', '789 Engine Blvd', 'London', 'England', 'NW1 6XE'),
(4, '1985-03-22', 'Female', '101 Island Rd', 'Gateway City', 'CA', '90210');

-- =========================================================
-- 3. DOCTOR
-- =========================================================
INSERT INTO DOCTOR (UserID, MedicalRegistrationNumber, Specialization)
VALUES 
(5, 'MED-REG-991', 'Cardiology'),
(6, 'MED-REG-992', 'General Medicine'),
(7, 'MED-REG-993', 'Neurology');

-- =========================================================
-- 4. CAREGIVER
-- =========================================================
INSERT INTO CAREGIVER (UserID)
VALUES (8), (9), (10), (11);

-- =========================================================
-- 5. CAREGIVER_PATIENT
-- =========================================================
INSERT INTO CAREGIVER_PATIENT (CaregiverID, PatientID, RelationshipToPatient)
VALUES 
(8, 1, 'Daughter'), -- Elena cares for Alan
(8, 2, 'Niece'),    -- Elena also cares for Barbara (Multiple patients)
(9, 3, 'Professional Nurse'),
(10, 4, 'Sister');

-- =========================================================
-- 6. MEDICINE
-- =========================================================
INSERT INTO MEDICINE (MedicineID, MedicineName, Strength, DosageForm, Manufacturer)
OVERRIDING SYSTEM VALUE VALUES 
(1, 'Paracetamol', '500mg', 'Tablet', 'PharmaCorp'),
(2, 'Amoxicillin', '250mg', 'Capsule', 'HealthPlus'),
(3, 'Lisinopril', '10mg', 'Tablet', 'HeartCare Meds'),
(4, 'Metformin', '500mg', 'Tablet', 'GlucoMeds'),
(5, 'Atorvastatin', '20mg', 'Tablet', 'HeartCare Meds'),
(6, 'Omeprazole', '20mg', 'Capsule', 'GastroHealth'),
(7, 'Levothyroxine', '50mcg', 'Tablet', 'EndoPharma'),
(8, 'Ibuprofen', '400mg', 'Tablet', 'PharmaCorp');

-- =========================================================
-- 7. PRESCRIPTION
-- =========================================================
INSERT INTO PRESCRIPTION (PrescriptionID, PatientID, DoctorID, PrescriptionDate, StartDate, EndDate)
OVERRIDING SYSTEM VALUE VALUES 
(1, 1, 5, '2026-08-01', '2026-08-01', '2026-08-31'), -- Alan's Heart meds
(2, 1, 6, '2026-08-05', '2026-08-05', '2026-08-15'), -- Alan's Pain meds (Multiple Prescriptions)
(3, 2, 6, '2026-07-20', '2026-07-20', '2026-10-20'), -- Barbara's Diabetes meds
(4, 3, 7, '2026-08-10', '2026-08-10', '2026-09-10'), -- Charles's Neuro meds
(5, 4, 6, '2026-08-15', '2026-08-15', '2026-08-22'); -- Diana's Antibiotics

-- =========================================================
-- 8. PRESCRIPTION ITEM
-- =========================================================
INSERT INTO PRESCRIPTION_ITEM (PrescriptionItemID, PrescriptionID, MedicineID, Dosage, Frequency, Duration)
OVERRIDING SYSTEM VALUE VALUES 
(1, 1, 3, '1 Tablet', 'Once daily', '30 Days'), -- Lisinopril
(2, 1, 5, '1 Tablet', 'Once daily at night', '30 Days'), -- Atorvastatin (Multiple items in P1)
(3, 2, 1, '1 Tablet', 'Every 8 hours PRN', '10 Days'), -- Paracetamol
(4, 3, 4, '1 Tablet', 'Twice daily with meals', '90 Days'), -- Metformin
(5, 4, 7, '1 Tablet', 'Once daily morning empty stomach', '30 Days'), -- Levothyroxine
(6, 5, 2, '1 Capsule', 'Every 8 hours', '7 Days'), -- Amoxicillin
(7, 5, 8, '1 Tablet', 'Every 6 hours PRN', '7 Days'); -- Ibuprofen

-- =========================================================
-- 9. MEDICINE BATCH (BCNF Implementation)
-- =========================================================
INSERT INTO MEDICINE_BATCH (MedicineID, BatchNumber, ExpiryDate)
VALUES 
(1, 'PAR-EXP-01', '2026-01-15'), -- Intentionally EXPIRED
(1, 'PAR-NEW-02', '2027-12-31'), -- Healthy batch (Multiple batches for Med 1)
(2, 'AMX-101', '2027-05-01'),
(3, 'LIS-101', '2028-02-28'),
(4, 'MET-LOW-01', '2027-06-30'), -- Will be low stock
(4, 'MET-NEW-02', '2028-06-30'), 
(5, 'ATO-101', '2027-11-30'),
(6, 'OME-101', '2028-01-15'),
(7, 'LEV-101', '2027-09-30'),
(8, 'IBU-101', '2027-03-31');

-- =========================================================
-- 10. INVENTORY
-- =========================================================
INSERT INTO INVENTORY (InventoryID, MedicineID, BatchNumber, QuantityAvailable, MinimumStockLevel)
OVERRIDING SYSTEM VALUE VALUES 
(1, 1, 'PAR-EXP-01', 50, 20), -- Expired paracetamol sitting in inventory
(2, 1, 'PAR-NEW-02', 200, 50), -- Healthy paracetamol
(3, 2, 'AMX-101', 100, 30),
(4, 3, 'LIS-101', 120, 25),
(5, 4, 'MET-LOW-01', 5, 20), -- LOW STOCK Condition (5 < 20)
(6, 5, 'ATO-101', 90, 20),
(7, 6, 'OME-101', 150, 30),
(8, 7, 'LEV-101', 100, 20),
(9, 8, 'IBU-101', 80, 20);

-- =========================================================
-- 11. DISPENSER SLOT
-- =========================================================
INSERT INTO DISPENSER_SLOT (SlotID, SlotNumber, Capacity)
OVERRIDING SYSTEM VALUE VALUES 
(1, 1, 200), (2, 2, 200), (3, 3, 200), (4, 4, 150),
(5, 5, 150), (6, 6, 150), (7, 7, 100), (8, 8, 100),
(9, 9, 100), (10, 10, 50), (11, 11, 50), (12, 12, 50);

-- =========================================================
-- 12. INVENTORY_SLOT
-- =========================================================
INSERT INTO INVENTORY_SLOT (InventoryID, SlotID)
VALUES 
(1, 1), (2, 2), (3, 3), (4, 4), 
(5, 5), (6, 6), (7, 7), (8, 8), (9, 9); 
-- Slots 10, 11, 12 remain empty

-- =========================================================
-- 13. DISPENSE SCHEDULE
-- =========================================================
-- Creating schedules across different days for demonstration
INSERT INTO DISPENSE_SCHEDULE (ScheduleID, PrescriptionItemID, ScheduledTime, QuantityToDispense, StartDate, EndDate)
OVERRIDING SYSTEM VALUE VALUES 
(1, 1, '08:00:00', 1, '2026-08-01', '2026-08-31'), -- Lisinopril Morning
(2, 2, '20:00:00', 1, '2026-08-01', '2026-08-31'), -- Atorvastatin Night
(3, 4, '09:00:00', 1, '2026-07-20', '2026-10-20'), -- Metformin Morning
(4, 4, '21:00:00', 1, '2026-07-20', '2026-10-20'), -- Metformin Night
(5, 6, '08:00:00', 1, '2026-08-15', '2026-08-22'), -- Amoxicillin 1
(6, 6, '16:00:00', 1, '2026-08-15', '2026-08-22'), -- Amoxicillin 2
(7, 6, '23:59:00', 1, '2026-08-15', '2026-08-22'); -- Amoxicillin 3

-- =========================================================
-- 14. DISPENSE LOG
-- =========================================================
INSERT INTO DISPENSE_LOG (DispenseID, ScheduleID, DispenseDateTime, QuantityDispensed, Status, FailureReason)
OVERRIDING SYSTEM VALUE VALUES 
-- Schedule 1 (Lisinopril) over three days
(1, 1, '2026-08-18 08:00:15+05:30', 1, 'SUCCESS', NULL),
(2, 1, '2026-08-19 08:02:10+05:30', 1, 'SUCCESS', NULL),
(3, 1, '2026-08-20 08:00:05+05:30', 0, 'FAILED', 'MOTOR_JAM_ERROR_CODE_4'), 

-- Schedule 2 (Atorvastatin)
(4, 2, '2026-08-18 20:05:00+05:30', 1, 'SUCCESS', NULL),
(5, 2, '2026-08-19 20:01:00+05:30', 1, 'SUCCESS', NULL),

-- Schedule 3 & 4 (Metformin - The low stock item)
(6, 3, '2026-08-20 09:00:20+05:30', 1, 'SUCCESS', NULL),
(7, 4, '2026-08-20 21:00:00+05:30', 1, 'SUCCESS', NULL),
(8, 3, '2026-08-21 09:00:00+05:30', 0, 'FAILED', 'SLOT_EMPTY_PLEASE_REFILL'),

-- Schedule 5 (Amoxicillin) - Demonstrating a partial dispense (e.g., requested 2, dispensed 1)
-- Adjusting schedule 5 history to simulate a scenario where it tried to dispense 2 but failed halfway.
(9, 5, '2026-08-15 08:01:00+05:30', 1, 'SUCCESS', NULL),
(10, 6, '2026-08-15 16:00:30+05:30', 1, 'SUCCESS', NULL),
(11, 7, '2026-08-15 23:59:45+05:30', 0, 'PARTIAL', 'PILL_STUCK_IN_CHUTE');

-- Reset sequences for future manual inserts so they don't crash
SELECT setval(pg_get_serial_sequence('"USER"', 'userid'), coalesce(max(userid), 1) + 1, false) FROM "USER";
SELECT setval(pg_get_serial_sequence('MEDICINE', 'medicineid'), coalesce(max(medicineid), 1) + 1, false) FROM MEDICINE;
SELECT setval(pg_get_serial_sequence('PRESCRIPTION', 'prescriptionid'), coalesce(max(prescriptionid), 1) + 1, false) FROM PRESCRIPTION;
SELECT setval(pg_get_serial_sequence('PRESCRIPTION_ITEM', 'prescriptionitemid'), coalesce(max(prescriptionitemid), 1) + 1, false) FROM PRESCRIPTION_ITEM;
SELECT setval(pg_get_serial_sequence('INVENTORY', 'inventoryid'), coalesce(max(inventoryid), 1) + 1, false) FROM INVENTORY;
SELECT setval(pg_get_serial_sequence('DISPENSER_SLOT', 'slotid'), coalesce(max(slotid), 1) + 1, false) FROM DISPENSER_SLOT;
SELECT setval(pg_get_serial_sequence('DISPENSE_SCHEDULE', 'scheduleid'), coalesce(max(scheduleid), 1) + 1, false) FROM DISPENSE_SCHEDULE;
SELECT setval(pg_get_serial_sequence('DISPENSE_LOG', 'dispenseid'), coalesce(max(dispenseid), 1) + 1, false) FROM DISPENSE_LOG;

COMMIT;