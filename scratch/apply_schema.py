import os
from sqlalchemy import text
from backend.database import engine
from backend.seed import seed_db

with engine.connect() as conn:
    print('Dropping tables...')
    with open('schema/schema.sql', 'r') as f:
        schema_sql = f.read()

    tables = ['NFC_CARD', 'DISPENSE_LOG', 'DISPENSE_SCHEDULE', 'INVENTORY_SLOT', 'DISPENSER_SLOT', 'INVENTORY', 'MEDICINE_BATCH', 'PRESCRIPTION_ITEM', 'PRESCRIPTION', 'MEDICINE', 'CAREGIVER_PATIENT', 'CAREGIVER', 'DOCTOR', 'PATIENT', '"USER"']
    for t in tables:
        conn.execute(text(f'DROP TABLE IF EXISTS {t} CASCADE;'))
    
    print('Applying schema...')
    conn.execute(text(schema_sql))
    conn.commit()

print('Schema applied. Seeding...')
seed_db()
print('Done!')
