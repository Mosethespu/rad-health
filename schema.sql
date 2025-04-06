DROP TABLE IF EXISTS admins;
CREATE TABLE admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT,
    phone_number TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    registered_doctor_id INTEGER,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registered_doctor_id) REFERENCES doctors(doctor_id)
);

DROP TABLE IF EXISTS doctors;
CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL,
    specialization TEXT,
    phone_number TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS receptionists;
CREATE TABLE receptionists (
    receptionist_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL,
    phone_number TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_datetime DATETIME NOT NULL,
    booking_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancellation_datetime TIMESTAMP,
    is_cancelled BOOLEAN DEFAULT 0,
    has_checked_in BOOLEAN DEFAULT 0,
    outcome TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

DROP TABLE IF EXISTS prescriptions;
CREATE TABLE prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    appointment_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    prescription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    medication_name TEXT NOT NULL,
    dosage TEXT,
    notes TEXT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

DROP TABLE IF EXISTS triage;
CREATE TABLE triage (
    triage_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    appointment_id INTEGER UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL,
    receptionist_id INTEGER,
    triage_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    symptoms TEXT,
    blood_pressure TEXT,
    temperature REAL,
    pulse_rate INTEGER,
    notes TEXT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (receptionist_id) REFERENCES receptionists(receptionist_id)
);

DROP TABLE IF EXISTS nurses;
CREATE TABLE nurses (
    nurse_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL,
    phone_number TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);