# Rad Health Center

Rad Health Center is a healthcare management system designed to streamline operations for healthcare centers. It includes functionalities for Admin, Receptionist, Doctor, Nurse, and Patient roles.

---

## **Features**
- **Admin**: Manage staff, view records, and oversee the system.
- **Receptionist**: Register/deregister patients, manage appointments, and check patient records.
- **Doctor**: View appointments, manage patient records, and prescribe medications.
- **Nurse**: Perform triage and manage patient vitals.
- **Patient**: Book appointments, view medical records, and manage their profile.

---

## **Prerequisites**
Before running the program, ensure the following are installed on your system:
1. **Python 3.8 or higher**: [Download Python](https://www.python.org/downloads/)
2. **SQLite**: Pre-installed on most systems. Verify by running:
   ```bash
   sqlite3 --version
   ```
3. **Pip**: Python package manager. Verify by running:
   ```bash
   pip --version
   ```
4. **Virtual Environment (Optional)**: Recommended for dependency isolation.

---

## **Dependencies**
The following Python libraries are required:
- **Flask**: Web framework
- **SQLite3**: Database integration
- **Faker**: Generate fake data for testing
- **Selenium**: For system testing (optional)

Install all dependencies using the following command:
```bash
pip install -r requirements.txt
```

---

## **Setup Instructions**

### **Step 1: Clone the Repository**
Clone the project repository to your local machine:
```bash
git clone https://github.com/YourGitHubUsername/rad-health.git
cd rad-health
```

### **Step 2: Set Up the Database**
Initialize the SQLite database:
```bash
flask initdb
```
This will create the `database.db` file and populate it with the required tables and an initial admin account:
- **Username**: `admin`
- **Password**: `admin123`

### **Step 3: Run the Application**
Start the Flask development server:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

---

## **Platform-Specific Instructions**

### **Windows**
1. Install Python from [python.org](https://www.python.org/downloads/).
2. Add Python to your system's PATH during installation.
3. Open Command Prompt and follow the setup instructions above.

### **Linux**
1. Install Python using your package manager:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Follow the setup instructions above.

### **MacOS**
1. Install Python using Homebrew:
   ```bash
   brew install python
   ```
2. Follow the setup instructions above.

---

## **Testing the Application**

### **Unit Testing**
Run unit tests to verify individual components:
```bash
python -m unittest discover -s tests -p "test_unit.py"
```

### **Integration Testing**
Run integration tests to verify module interactions:
```bash
python -m unittest discover -s tests -p "test_integration.py"
```

### **System Testing**
Run system tests using Selenium (ensure the Flask server is running):
```bash
python -m unittest discover -s tests -p "test_system.py"
```

---

## **Default Roles and Credentials**
The following roles and credentials are available for testing:

| **Role**         | **Username** | **Password** |
|-------------------|--------------|--------------|
| Admin            | admin        | admin123     |
| Receptionist     | rrecept_linda1 | receptpass1  |
| Doctor           | doc_john1     | password123  |
| Nurse            | nurse_elizabeth1   | nursepass1  |
| Patient          | george10 | patient1  |

---

## **Folder Structure**
```
rad-health/
├── app.py                  # Main application file
├── schema.sql              # Database schema
├── populate_db.py          # Script to populate the database with fake data
├── templates/              # HTML templates for the web app
├── static/                 # Static files (CSS, JS, images)
├── tests/                  # Unit, integration, and system tests
└── README.md               # Project documentation
```

---

## **Populating the Database with Fake Data**
To populate the database with fake data for testing, run:
```bash
python populate_db.py
```
This will create:
- 50 patients
- 20 doctors
- 10 nurses
- 5 receptionists
- 50 appointments with various statuses

---

## **Troubleshooting**
1. **Flask Command Not Found**:
   Ensure Python and Pip are installed correctly. Activate your virtual environment if using one.
2. **Database Errors**:
   Delete the `database.db` file and reinitialize the database:
   ```bash
   rm database.db
   flask initdb
   ```
3. **Selenium Errors**:
   Ensure you have the appropriate WebDriver installed for your browser (e.g., ChromeDriver for Google Chrome).

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contributing**
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## **Contact**
For any questions or issues, please contact:
- **Email**: bobitnrb339117@spu.ac.ke
- **GitHub**: [Mosethespu](https://github.com/YourGitHubUsername)