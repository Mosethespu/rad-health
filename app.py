from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import secrets  # For generating random passwords

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Remember to use a strong, random key

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(conn):
    if conn:
        conn.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())

        # Create the initial admin user if it doesn't exist
        cursor = db.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", ('admin',))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ('admin', 'admin123')) # Use a more secure password in production
            print("Initial admin account created: username='admin', password='admin123'")

        db.commit()
        close_db(db)

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        phone_number = request.form['phone_number']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO patients (name, date_of_birth, address, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name, date_of_birth, address, phone_number, email, username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already exists. Please choose another one."
            return render_template('signup.html', error=error)
        finally:
            close_db(conn)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        # Check admins
        admin = cursor.execute("SELECT admin_id, username, password FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and admin['password'] == password:
            session['user_id'] = admin['admin_id']
            session['username'] = username
            session['user_role'] = 'admin'
            close_db(conn)
            return redirect(url_for('admin_dashboard'))

        # Check patients
        patient = cursor.execute("SELECT patient_id, username, password, name FROM patients WHERE username = ?", (username,)).fetchone()
        if patient and patient['password'] == password:
            session['user_id'] = patient['patient_id']
            session['username'] = patient['name']
            session['user_role'] = 'patient'
            close_db(conn)
            return redirect(url_for('patient_dashboard'))

        # Check doctors
        doctor = cursor.execute("SELECT doctor_id, username, password, name FROM doctors WHERE username = ?", (username,)).fetchone()
        if doctor and doctor['password'] == password:
            session['user_id'] = doctor['doctor_id']
            session['username'] = doctor['name']
            session['user_role'] = 'doctor'
            close_db(conn)
            return redirect(url_for('doctor_dashboard'))

        # Check receptionists
        receptionist = cursor.execute("SELECT receptionist_id, username, password, name FROM receptionists WHERE username = ?", (username,)).fetchone()
        if receptionist and receptionist['password'] == password:
            session['user_id'] = receptionist['receptionist_id']
            session['username'] = receptionist['name']
            session['user_role'] = 'receptionist'
            close_db(conn)
            return redirect(url_for('receptionist_dashboard'))

        # Check nurses (triage)
        nurse = cursor.execute("SELECT nurse_id, username, password, name FROM nurses WHERE username = ?", (username,)).fetchone()
        if nurse and nurse['password'] == password:
            session['user_id'] = nurse['nurse_id']
            session['username'] = nurse['name']
            session['user_role'] = 'nurse'
            close_db(conn)
            return redirect(url_for('nurse_dashboard'))

        close_db(conn)
        error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    return redirect(url_for('index'))

def login_required(role):
    def wrapper(fn):
        from functools import wraps
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not session.get('user_id') or session.get('user_role') != role:
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

#@app.route('/patient/dashboard')
#@login_required('patient')
#def patient_dashboard():
#    return render_template('patient_dashboard.html')

#@app.route('/doctor/dashboard')
#@login_required('doctor')
#def doctor_dashboard():
#    return render_template('doctor_dashboard.html')

# ... (Import statements and basic app setup)

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/create_staff/<string:role>', methods=['GET', 'POST'])
@login_required('admin')
def create_staff(role):
    if role not in ['doctor', 'receptionist', 'nurse']:
        return "Invalid staff role."

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        email = request.form['email']

        conn = get_db()
        cursor = conn.cursor()
        error = None

        try:
            if role == 'doctor':
                specialization = request.form.get('specialization')
                cursor.execute("INSERT INTO doctors (name, username, password, specialization, phone_number, email) VALUES (?, ?, ?, ?, ?, ?)",
                               (name, username, password, specialization, phone_number, email))
            elif role == 'receptionist':
                cursor.execute("INSERT INTO receptionists (name, username, password, phone_number, email) VALUES (?, ?, ?, ?, ?)",
                               (name, username, password, phone_number, email))
            elif role == 'nurse':
                cursor.execute("INSERT INTO nurses (name, username, password, phone_number, email) VALUES (?, ?, ?, ?, ?)",
                               (name, username, password, phone_number, email))
            conn.commit()
            return redirect(url_for('admin_dashboard'))
        except sqlite3.IntegrityError:
            error = f"Username '{username}' is already taken."
        finally:
            close_db(conn)

        return render_template('create_staff.html', role=role, error=error)

    return render_template('create_staff.html', role=role)

# ... (Rest of your app.py code)

@app.route('/receptionist/dashboard')
@login_required('receptionist')
def receptionist_dashboard():
    return render_template('receptionist_dashboard.html')

# ... (Import statements and basic app setup)

@app.route('/receptionist/register_patient', methods=['GET', 'POST'])
@login_required('receptionist')
def register_patient():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        date_of_birth = request.form['date_of_birth']
        address = request.form['address']
        phone_number = request.form['phone_number']
        email = request.form['email']

        # Generate a simple username and password
        generated_username = name.lower().replace(' ', '') + str(secrets.token_hex(2))[:6]
        generated_password = secrets.token_urlsafe(8)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO patients (name, date_of_birth, address, phone_number, email, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name, date_of_birth, address, phone_number, email, generated_username, generated_password))
            conn.commit()
            message = f"Patient registered successfully. Username: {generated_username}, Password: {generated_password}"
            return render_template('register_patient.html', message=message)
        except sqlite3.IntegrityError:
            error = "Could not register patient. Username might already exist."
        finally:
            close_db(conn)
    return render_template('register_patient.html', error=error)

@app.route('/receptionist/deregister_patient', methods=['GET', 'POST'])
@login_required('receptionist')
def deregister_patient():
    message = None
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE patients SET username = NULL, password = NULL WHERE patient_id = ?", (patient_id,))
            conn.commit()
            message = f"Patient with ID {patient_id} has been deregistered."
        except sqlite3.Error as e:
            message = f"Error deregistering patient: {e}"
        finally:
            close_db(conn)
    return render_template('deregister_patient.html', message=message)

@app.route('/receptionist/check_patient', methods=['GET'])
@login_required('receptionist')
def check_patient():
    patient_details = None
    appointments = None
    patient_identifier = request.args.get('patient_identifier')

    if patient_identifier:
        conn = get_db()
        cursor = conn.cursor()

        # Search by patient ID or name
        cursor.execute("SELECT * FROM patients WHERE patient_id = ? OR name LIKE ?", (patient_identifier, f"%{patient_identifier}%"))
        patient_details = cursor.fetchone()

        if patient_details:
            cursor.execute("""
                SELECT a.appointment_id, a.appointment_datetime, d.name AS doctor_name, a.is_cancelled, a.has_checked_in
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = ?
            """, (patient_details['patient_id'],))
            appointments = cursor.fetchall()

        close_db(conn)

    return render_template('check_patient.html', patient_details=patient_details, appointments=appointments)

@app.route('/receptionist/create_appointment', methods=['GET', 'POST'])
@login_required('receptionist')
def create_appointment():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        appointment_datetime_str = request.form['appointment_datetime']

        conn = get_db()
        cursor = conn.cursor()

        # Check for conflicting appointments (basic check)
        cursor.execute("SELECT * FROM appointments WHERE doctor_id = ? AND appointment_datetime = ?", (doctor_id, appointment_datetime_str))
        conflicting_appointment = cursor.fetchone()

        if conflicting_appointment:
            error = "This doctor is already booked at that time."
            close_db(conn)
            return render_template('create_appointment.html', error=error)
        else:
            try:
                cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_datetime) VALUES (?, ?, ?)",
                               (patient_id, doctor_id, appointment_datetime_str))
                conn.commit()
                close_db(conn)
                message = "Appointment created successfully."
                return render_template('create_appointment.html', message=message)
            except sqlite3.IntegrityError:
                error = "Could not create appointment. Patient or Doctor ID might be invalid."
                close_db(conn)
                return render_template('create_appointment.html', error=error)

    return render_template('create_appointment.html')

# ... (Rest of your app.py code)

# ... (Import statements and basic app setup)

@app.route('/nurse/dashboard')
@login_required('nurse')
def nurse_dashboard():
    return render_template('nurse_dashboard.html')

@app.route('/nurse/pending_triage')
@login_required('nurse')
def view_pending_triage():
    conn = get_db()
    cursor = conn.cursor()
    # Get appointments that have checked in but haven't had triage yet (you might need to add a status to appointments)
    # For now, let's assume appointments without triage records are pending
    cursor.execute("""
        SELECT a.appointment_id, p.name AS patient_name, a.appointment_datetime
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN triage t ON a.appointment_id = t.appointment_id
        WHERE a.has_checked_in = 1 AND t.triage_id IS NULL
    """)
    appointments = cursor.fetchall()
    close_db(conn)
    return render_template('view_pending_triage.html', appointments=appointments)

@app.route('/nurse/perform_triage/<int:appointment_id>', methods=['GET', 'POST'])
@login_required('nurse')
def perform_triage(appointment_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_id = ?", (appointment_id,))
    appointment = cursor.fetchone()
    if not appointment:
        close_db(conn)
        return "Appointment not found."
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (appointment['patient_id'],))
    patient = cursor.fetchone()
    if not patient:
        close_db(conn)
        return "Patient not found."

    if request.method == 'POST':
        symptoms = request.form['symptoms']
        blood_pressure = request.form['blood_pressure']
        temperature = request.form['temperature']
        pulse_rate = request.form['pulse_rate']
        notes = request.form['notes']
        nurse_id = session['user_id'] # Assuming nurse_id in session

        try:
            cursor.execute("""
                INSERT INTO triage (appointment_id, patient_id, receptionist_id, symptoms, blood_pressure, temperature, pulse_rate, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient['patient_id'], nurse_id, symptoms, blood_pressure, temperature, pulse_rate, notes))
            conn.commit()
            close_db(conn)
            return redirect(url_for('view_pending_triage')) # Redirect back to the pending list
        except sqlite3.Error as e:
            close_db(conn)
            return f"Error recording triage: {e}"

    close_db(conn)
    return render_template('perform_triage.html', appointment=appointment, patient=patient)

# ... (Rest of your app.py code)

# ... (Import statements and basic app setup)

@app.route('/doctor/dashboard')
@login_required('doctor')
def doctor_dashboard():
    return render_template('doctor_dashboard.html')

@app.route('/doctor/appointments/<string:status>')
@login_required('doctor')
def doctor_view_appointments(status):
    conn = get_db()
    cursor = conn.cursor()
    doctor_id = session['user_id']
    appointments = []
    appointment_title = ""

    if status == 'today':
        # Implement logic to fetch today's appointments for the doctor
        appointment_title = "Today's Appointments"
    elif status == 'upcoming':
        # Implement logic to fetch upcoming appointments
        appointment_title = "Upcoming Appointments"
    elif status == 'past':
        # Implement logic to fetch past appointments
        appointment_title = "Past Appointments"
    elif status == 'active':
        # Implement logic to fetch appointments ready for consultation (after triage)
        cursor.execute("""
            SELECT a.appointment_id, p.name AS patient_name, a.appointment_datetime
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN triage t ON a.appointment_id = t.appointment_id
            WHERE a.doctor_id = ? AND a.has_checked_in = 1 AND t.triage_id IS NOT NULL
        """, (doctor_id,))
        appointments = cursor.fetchall()
        appointment_title = "Active Appointments"

    close_db(conn)
    return render_template('doctor_view_appointments.html', appointments=appointments, appointment_title=appointment_title, status=status)

@app.route('/doctor/patient_record/<int:appointment_id>', methods=['GET', 'POST'])
@login_required('doctor')
def view_patient_record(appointment_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_id = ?", (appointment_id,))
    appointment = cursor.fetchone()
    if not appointment:
        close_db(conn)
        return "Appointment not found."
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (appointment['patient_id'],))
    patient = cursor.fetchone()
    if not patient:
        close_db(conn)
        return "Patient not found."
    cursor.execute("SELECT * FROM triage WHERE appointment_id = ?", (appointment_id,))
    triage = cursor.fetchone()

    if request.method == 'POST':
        outcome = request.form['outcome']
        medication_name = request.form.get('medication_name')
        dosage = request.form.get('dosage')
        prescription_notes = request.form.get('prescription_notes')
        doctor_id = session['user_id']

        cursor.execute("UPDATE appointments SET outcome = ? WHERE appointment_id = ?", (outcome, appointment_id))
        if medication_name:
            cursor.execute("""
                INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, medication_name, dosage, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient['patient_id'], doctor_id, medication_name, dosage, prescription_notes))
        conn.commit()
        close_db(conn)
        return redirect(url_for('doctor_view_appointments', status='active')) # Redirect back to active appointments

    close_db(conn)
    return render_template('view_patient_record.html', appointment=appointment, patient=patient, triage=triage)

@app.route('/doctor/emergency_appointment/<string:service_type>', methods=['GET', 'POST'])
@login_required('doctor')
def create_emergency_appointment(service_type):
    if request.method == 'POST':
        patient_identifier = request.form['patient_identifier']
        # Implement logic to find or create a patient based on the identifier
        # Then create the emergency appointment record
        return "Emergency appointment created (logic to be implemented)"
    return render_template('create_emergency_appointment.html', service_type=service_type)

# ... (Rest of your app.py code)

# ... (Import statements and basic app setup)

@app.route('/patient/dashboard')
@login_required('patient')
def patient_dashboard():
    return render_template('patient_dashboard.html')

@app.route('/patient/appointments/<string:status>')
@login_required('patient')
def patient_view_appointments(status):
    conn = get_db()
    cursor = conn.cursor()
    patient_id = session['user_id']
    appointments = []
    if status == 'upcoming':
        cursor.execute("SELECT * FROM appointments WHERE patient_id = ? AND appointment_datetime > datetime('now') AND is_cancelled = 0", (patient_id,))
    elif status == 'past':
        cursor.execute("SELECT * FROM appointments WHERE patient_id = ? AND appointment_datetime <= datetime('now')", (patient_id,))
    appointments = cursor.fetchall()
    close_db(conn)
    return render_template('patient_view_appointments.html', appointments=appointments, status=status)

@app.route('/patient/cancel_appointment/<int:appointment_id>')
@login_required('patient')
def patient_cancel_appointment(appointment_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET is_cancelled = 1, cancellation_datetime = datetime('now') WHERE appointment_id = ? AND patient_id = ?", (appointment_id, session['user_id']))
    conn.commit()
    close_db(conn)
    return redirect(url_for('patient_view_appointments', status='upcoming'))

@app.route('/patient/records')
@login_required('patient')
def patient_view_records():
    conn = get_db()
    cursor = conn.cursor()
    patient_id = session['user_id']
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_datetime, a.outcome, p.medication_name, p.dosage
        FROM appointments a
        LEFT JOIN prescriptions p ON a.appointment_id = p.appointment_id
        WHERE a.patient_id = ?
    """, (patient_id,))
    records = cursor.fetchall()
    close_db(conn)
    return render_template('patient_view_records.html', records=records)

@app.route('/patient/book_appointment', methods=['GET', 'POST'])
@login_required('patient')
def patient_book_appointment():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_datetime_str = request.form['appointment_datetime']
        patient_id = session['user_id']

        conn = get_db()
        cursor = conn.cursor()

        # Basic check for conflicting appointments (can be expanded)
        if doctor_id:
            cursor.execute("SELECT * FROM appointments WHERE doctor_id = ? AND appointment_datetime = ?", (doctor_id, appointment_datetime_str))
        else:
            # Find any available doctor (more complex logic needed for real availability)
            cursor.execute("SELECT doctor_id FROM doctors LIMIT 1") # Just get one for now
            available_doctor = cursor.fetchone()
            doctor_id = available_doctor['doctor_id'] if available_doctor else None

        if doctor_id:
            try:
                cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_datetime) VALUES (?, ?, ?)",
                               (patient_id, doctor_id, appointment_datetime_str))
                conn.commit()
                close_db(conn)
                message = "Appointment requested successfully."
                return render_template('patient_book_appointment.html', message=message)
            except sqlite3.IntegrityError:
                error = "Could not book appointment."
                close_db(conn)
                return render_template('patient_book_appointment.html', error=error)
        else:
            close_db(conn)
            return render_template('patient_book_appointment.html', error="No doctors available.")

    return render_template('patient_book_appointment.html')

# ... (Rest of your app.py code)

@app.route('/admin/view_records/<string:record_type>', methods=['GET'])
@login_required('admin')
def view_records(record_type):
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of records per page
    offset = (page - 1) * per_page

    conn = get_db()
    cursor = conn.cursor()

    if record_type == 'patients':
        cursor.execute("SELECT * FROM patients LIMIT ? OFFSET ?", (per_page, offset))
        records = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_records = cursor.fetchone()[0]
    elif record_type == 'staff':
        cursor.execute("""
            SELECT 'Doctor' AS role, name, username, email FROM doctors
            UNION ALL
            SELECT 'Nurse' AS role, name, username, email FROM nurses
            UNION ALL
            SELECT 'Receptionist' AS role, name, username, email FROM receptionists
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        records = cursor.fetchall()
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT doctor_id FROM doctors
                UNION ALL
                SELECT nurse_id FROM nurses
                UNION ALL
                SELECT receptionist_id FROM receptionists
            )
        """)
        total_records = cursor.fetchone()[0]
    else:
        close_db(conn)
        return "Invalid record type."

    total_pages = (total_records + per_page - 1) // per_page
    close_db(conn)

    return render_template('view_records.html', records=records, record_type=record_type, page=page, total_pages=total_pages)

@app.route('/admin/view_prescriptions', methods=['GET'])
@login_required('admin')
def view_prescriptions():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.prescription_id, p.medication_name, p.dosage, p.notes, pa.name AS patient_name, d.name AS doctor_name
        FROM prescriptions p
        JOIN patients pa ON p.patient_id = pa.patient_id
        JOIN doctors d ON p.doctor_id = d.doctor_id
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    prescriptions = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM prescriptions")
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    close_db(conn)
    return render_template('view_prescriptions.html', prescriptions=prescriptions, page=page, total_pages=total_pages)


@app.route('/admin/view_appointments', methods=['GET'])
@login_required('admin')
def view_appointments():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.appointment_id, pa.name AS patient_name, d.name AS doctor_name, a.appointment_datetime, 
               a.is_cancelled, a.has_checked_in, a.outcome
        FROM appointments a
        JOIN patients pa ON a.patient_id = pa.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    appointments = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    close_db(conn)
    return render_template('view_appointments.html', appointments=appointments, page=page, total_pages=total_pages)

@app.route('/receptionist/view_appointments/<string:timeframe>', methods=['GET'])
@login_required('receptionist')
def receptionist_view_appointments(timeframe):
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name, a.appointment_datetime, 
               a.is_cancelled, a.has_checked_in
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """
    conditions = []
    params = []

    if timeframe == 'daily':
        conditions.append("DATE(a.appointment_datetime) = DATE('now')")
    elif timeframe == 'weekly':
        conditions.append("DATE(a.appointment_datetime) BETWEEN DATE('now', 'weekday 0', '-7 days') AND DATE('now', 'weekday 0')")
    elif timeframe == 'monthly':
        conditions.append("strftime('%Y-%m', a.appointment_datetime) = strftime('%Y-%m', 'now')")
    elif timeframe == 'past':
        conditions.append("a.appointment_datetime < datetime('now')")
    elif timeframe == 'active':
        conditions.append("a.has_checked_in = 1 AND a.is_cancelled = 0")
    elif timeframe == 'future':
        conditions.append("a.appointment_datetime > datetime('now') AND a.is_cancelled = 0")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    appointments = cursor.fetchall()
    close_db(conn)

    return render_template('receptionist_view_appointments.html', appointments=appointments, timeframe=timeframe)

@app.route('/receptionist/check_in/<int:appointment_id>', methods=['POST'])
@login_required('receptionist')
def check_in_patient(appointment_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE appointments SET has_checked_in = 1 WHERE appointment_id = ?", (appointment_id,))
        conn.commit()
    except sqlite3.Error as e:
        return f"Error checking in patient: {e}"
    finally:
        close_db(conn)

    return redirect(url_for('view_all_appointments'))

@app.route('/receptionist/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required('receptionist')
def cancel_appointment(appointment_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE appointments SET is_cancelled = 1 WHERE appointment_id = ?", (appointment_id,))
        conn.commit()
    except sqlite3.Error as e:
        return f"Error cancelling appointment: {e}"
    finally:
        close_db(conn)

    return redirect(url_for('view_all_appointments'))

@app.route('/receptionist/view_all_appointments', methods=['GET', 'POST'])
@login_required('receptionist')
def view_all_appointments():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db()
    cursor = conn.cursor()

    # Base query
    query = """
        SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name, a.appointment_datetime, 
               a.is_cancelled, a.has_checked_in
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """
    params = []

    # Add search filter
    if search_query:
        query += " WHERE p.name LIKE ? OR d.name LIKE ? OR a.appointment_datetime LIKE ?"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    query += " ORDER BY a.appointment_datetime DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    appointments = cursor.fetchall()

    # Get total count for pagination
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    close_db(conn)

    return render_template('view_all_appointments.html', appointments=appointments, page=page, total_pages=total_pages, search_query=search_query)

if __name__ == '__main__':
    # Check if database exists, if not, initialize
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
            print("Database initialized on first run.")
    app.run(debug=True)