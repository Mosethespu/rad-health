import unittest
from app import get_db, close_db

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Set up a test database
        self.conn = get_db()
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.conn.commit()

    def tearDown(self):
        # Clean up the database after each test
        self.cursor.execute("DELETE FROM appointments;")
        self.cursor.execute("DELETE FROM patients;")
        self.cursor.execute("DELETE FROM doctors;")
        self.conn.commit()
        close_db(self.conn)

    def test_patient_registration_and_appointment(self):
        # Register a patient
        self.cursor.execute("""
            INSERT INTO patients (name, date_of_birth, address, phone_number, email, username, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Jane Doe", "1995-05-15", "456 Elm St", "9876543210", "jane@example.com", "janedoe", "password123"))
        self.conn.commit()

        # Create a doctor
        self.cursor.execute("""
            INSERT INTO doctors (name, username, password)
            VALUES (?, ?, ?)
        """, ("Dr. Brown", "drbrown", "password123"))
        self.conn.commit()

        # Create an appointment
        doctor_id = self.cursor.execute("SELECT doctor_id FROM doctors WHERE username = ?", ("drbrown",)).fetchone()["doctor_id"]
        patient_id = self.cursor.execute("SELECT patient_id FROM patients WHERE username = ?", ("janedoe",)).fetchone()["patient_id"]

        self.cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_datetime)
            VALUES (?, ?, ?)
        """, (patient_id, doctor_id, "2025-04-08 14:00:00"))
        self.conn.commit()

        # Verify the appointment
        self.cursor.execute("""
            SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ?
        """, (patient_id,))
        appointment = self.cursor.fetchone()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment["patient_name"], "Jane Doe")
        self.assertEqual(appointment["doctor_name"], "Dr. Brown")

if __name__ == "__main__":
    unittest.main()