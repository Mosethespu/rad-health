import unittest
from app import get_db, close_db

class TestUnit(unittest.TestCase):
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

    def test_create_patient(self):
        # Test inserting a new patient
        self.cursor.execute("""
            INSERT INTO patients (name, date_of_birth, address, phone_number, email, username, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("John Doe", "1990-01-01", "123 Main St", "1234567890", "john@example.com", "johndoe", "password123"))
        self.conn.commit()

        self.cursor.execute("SELECT * FROM patients WHERE username = ?", ("johndoe",))
        patient = self.cursor.fetchone()
        self.assertIsNotNone(patient)
        self.assertEqual(patient["name"], "John Doe")

    def test_create_appointment(self):
        # Test creating an appointment
        self.cursor.execute("""
            INSERT INTO doctors (name, username, password) VALUES (?, ?, ?)
        """, ("Dr. Smith", "drsmith", "password123"))
        self.cursor.execute("""
            INSERT INTO patients (name, username, password) VALUES (?, ?, ?)
        """, ("John Doe", "johndoe", "password123"))
        self.conn.commit()

        doctor_id = self.cursor.execute("SELECT doctor_id FROM doctors WHERE username = ?", ("drsmith",)).fetchone()["doctor_id"]
        patient_id = self.cursor.execute("SELECT patient_id FROM patients WHERE username = ?", ("johndoe",)).fetchone()["patient_id"]

        self.cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_datetime)
            VALUES (?, ?, ?)
        """, (patient_id, doctor_id, "2025-04-07 10:00:00"))
        self.conn.commit()

        self.cursor.execute("SELECT * FROM appointments WHERE patient_id = ?", (patient_id,))
        appointment = self.cursor.fetchone()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment["appointment_datetime"], "2025-04-07 10:00:00")

if __name__ == "__main__":
    unittest.main()