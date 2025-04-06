from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import unittest

class TestSystem(unittest.TestCase):
    def setUp(self):
        # Set up the Selenium WebDriver
        self.driver = webdriver.Chrome()

    def tearDown(self):
        # Close the browser after each test
        self.driver.quit()

    def test_patient_signup_and_login(self):
        driver = self.driver
        driver.get("http://localhost:5000/signup")

        # Fill out the signup form
        driver.find_element(By.ID, "name").send_keys("Alice Smith")
        driver.find_element(By.ID, "date_of_birth").send_keys("1990-01-01")
        driver.find_element(By.ID, "address").send_keys("789 Pine St")
        driver.find_element(By.ID, "phone_number").send_keys("1234567890")
        driver.find_element(By.ID, "email").send_keys("alice@example.com")
        driver.find_element(By.ID, "username").send_keys("alicesmith")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify redirection to login page
        self.assertIn("Login", driver.title)

        # Log in as the new patient
        driver.find_element(By.ID, "username").send_keys("alicesmith")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify redirection to patient dashboard
        self.assertIn("Patient Dashboard", driver.title)

if __name__ == "__main__":
    unittest.main()