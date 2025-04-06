import sqlite3
from datetime import datetime, timedelta
from faker import Faker
import random
import os  # Import the os module

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(conn):
    if conn:
        conn.close()

def init_db():
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.cursor().executescript(f.read())

    # Create the initial admin user if it doesn't exist
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", ('admin',))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ('admin', 'admin123')) # Use a more secure password in production
        print("Initial admin account created: username='admin', password='admin123'")

    conn.commit()
    close_db(conn)
    print('Initialized the database.')

fake = Faker('en_US') # Using US locale for realistic names and addresses

def create_fake_patient():
    name = fake.name()
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d')
    address = fake.address()
    phone_number = fake.phone_number()
    email = fake.email()
    username = fake.user_name() + str(random.randint(10, 99))
    password = fake.password(length=10)
    return (name, date_of_birth, address, phone_number, email, username, password)

def create_fake_doctor():
    name = f'Dr. {fake.name()}'
    specialization = random.choice(['General Practitioner', 'Cardiologist', 'Dermatologist', 'Neurologist', 'Pediatrician'])
    phone_number = fake.phone_number()
    email = fake.email()
    username = 'doc_' + fake.user_name() + str(random.randint(10, 99))
    password = fake.password(length=10)
    return (name, specialization, phone_number, email, username, password)

def create_fake_nurse():
    name = f'Nurse {fake.name()}'
    phone_number = fake.phone_number()
    email = fake.email()
    username = 'nurse_' + fake.user_name() + str(random.randint(10, 99))
    password = fake.password(length=10)
    return (name, phone_number, email, username, password)

def create_fake_receptionist():
    name = fake.name()
    phone_number = fake.phone_number()
    email = fake.email()
    username = 'recept_' + fake.user_name() + str(random.randint(10, 99))
    password = fake.password(length=10)
    return (name, phone_number, email, username, password)

def create_fake_appointment(patient_id, doctor_id, stage):
    now = datetime.now()
    future = now + timedelta(days=random.randint(1, 30))
    past = now - timedelta(days=random.randint(1, 30))
    appointment_datetime = random.choice([now, future, past]).isoformat()

    is_cancelled = 0
    has_checked_in = 0
    outcome = None
    medication_name = None
    dosage = None
    triage_data = None

    if stage == 'checked_in':
        has_checked_in = 1
    elif stage == 'triage_completed':
        has_checked_in = 1
        triage_data = (fake.text(max_nb_chars=100), fake.numerify(text='###') + '/' + fake.numerify(text='##'), random.uniform(36.0, 38.0), random.randint(60, 100), fake.text(max_nb_chars=50))
    elif stage == 'consultation_completed':
        has_checked_in = 1
        triage_data = (fake.text(max_nb_chars=100), fake.numerify(text='###') + '/' + fake.numerify(text='##'), random.uniform(36.0, 38.0), random.randint(60, 100), fake.text(max_nb_chars=50))
        outcome = fake.text(max_nb_chars=200)
        if random.random() < 0.7: # 70% chance of prescription
            medication_name = fake.word().capitalize()
            dosage = f'{random.randint(1, 3)} times a day'
    elif stage == 'cancelled':
        is_cancelled = 1

    return (patient_id, doctor_id, appointment_datetime, is_cancelled, has_checked_in, outcome, medication_name, dosage, triage_data)

if __name__ == '__main__':
    # Check if the database file exists, if not, create it and initialize the tables
    if not os.path.exists(DATABASE):
        print("Database file not found. Creating and initializing...")
        init_db()
    else:
        print("Database file already exists. Proceeding to populate data...")

    conn = get_db()
    cursor = conn.cursor()

    # Insert Doctors
    doctors_data = [create_fake_doctor() for _ in range(20)]
    cursor.executemany("INSERT INTO doctors (name, specialization, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?, ?)", doctors_data)
    doctor_ids = [row[0] for row in cursor.execute("SELECT doctor_id FROM doctors").fetchall()]
    print(f"Inserted {len(doctors_data)} doctors.")

    # Insert Nurses
    nurses_data = [create_fake_nurse() for _ in range(10)]
    cursor.executemany("INSERT INTO nurses (name, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?)", nurses_data)
    nurse_ids = [row[0] for row in cursor.execute("SELECT nurse_id FROM nurses").fetchall()]
    print(f"Inserted {len(nurses_data)} nurses.")

    # Insert Receptionists
    receptionists_data = [create_fake_receptionist() for _ in range(5)]
    cursor.executemany("INSERT INTO receptionists (name, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?)", receptionists_data)
    receptionist_ids = [row[0] for row in cursor.execute("SELECT receptionist_id FROM receptionists").fetchall()]
    print(f"Inserted {len(receptionists_data)} receptionists.")

    # Insert Patients
    patients_data = [create_fake_patient() for _ in range(50)]
    cursor.executemany("INSERT INTO patients (name, date_of_birth, address, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)", patients_data)
    patient_ids = [row[0] for row in cursor.execute("SELECT patient_id FROM patients").fetchall()]
    print(f"Inserted {len(patients_data)} patients.")

    # Insert Appointments with different stages
    appointment_stages = ['scheduled'] * 15 + ['checked_in'] * 10 + ['triage_completed'] * 10 + ['consultation_completed'] * 10 + ['cancelled'] * 5
    random.shuffle(appointment_stages)

    appointments_data = []
    for i in range(50):
        patient_id = random.choice(patient_ids)
        doctor_id = random.choice(doctor_ids)
        stage = appointment_stages[i]
        appointments_data.append(create_fake_appointment(patient_id, doctor_id, stage))

    for data in appointments_data:
        patient_id, doctor_id, appointment_datetime, is_cancelled, has_checked_in, outcome, medication_name, dosage, triage_data = data
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_datetime, is_cancelled, has_checked_in, outcome) VALUES (?, ?, ?, ?, ?, ?)",
                       (patient_id, doctor_id, appointment_datetime, is_cancelled, has_checked_in, outcome))
        appointment_id = cursor.lastrowid
        if medication_name:
            cursor.execute("INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, medication_name, dosage) VALUES (?, ?, ?, ?, ?)",
                           (appointment_id, patient_id, doctor_id, medication_name, dosage))
        if triage_data:
            symptoms, blood_pressure, temperature, pulse_rate, notes = triage_data
            # Assuming a receptionist and nurse might be involved in triage
            receptionist_id = random.choice(receptionist_ids) if receptionist_ids else None
            nurse_id = random.choice(nurse_ids) if nurse_ids else None
            cursor.execute("""
                INSERT INTO triage (appointment_id, patient_id, receptionist_id, symptoms, blood_pressure, temperature, pulse_rate, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient_id, receptionist_id, symptoms, blood_pressure, temperature, pulse_rate, notes))

    conn.commit()
    close_db(conn)
    print(f"Inserted {len(appointments_data)} appointments with various stages.")
    print("Database population complete!")