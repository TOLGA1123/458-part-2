import unittest
import time
import imaplib
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import email
import os
from dotenv import load_dotenv
load_dotenv()

#Click send once, then change content of the form, resend
class SendDifferentForm(unittest.TestCase):
    def setUp(self):
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "emulator-5554"
        options.platform_version = "16"
        options.app_package = "com.example.aisurveyapp"
        options.app_activity = ".LoginActivity"
        options.automation_name = "UiAutomator2"
        options.no_reset = True
        self.driver = webdriver.Remote("http://localhost:4723", options=options)
        self.driver.implicitly_wait(10)

    def test_basic_end_to_end_submission_different_sends(self):
        driver = self.driver

         # --- LOGIN PHASE ---
        email_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etUserInput"))
        )
        email_field.send_keys("admin@gmail.com")

        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etPassword"))
        )
        password_field.send_keys("password123")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogin"))
        )
        login_button.click()

        # --- MAIN ACTIVITY PHASE ---
        name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etName"))
        )
        name_field.send_keys("Test1")

        birth_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etBirthDate"))
        )
        birth_date_field.click()

        done_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))
        )
        done_button.click()

        spinner = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/spinnerEducation"))
        )
        spinner.click()
        time.sleep(2)

        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Bachelor\'s")').click()

        city_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etCity"))
        )
        city_field.send_keys("Ankara")

        female_radio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.RadioButton[@text='Female']"))
        )
        female_radio.click()

        chatgpt_checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/cbChatGPT"))
        )
        if chatgpt_checkbox.get_attribute("checked") != "true":
            chatgpt_checkbox.click()

        cons_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etChatGPTCons"))
        )
        cons_field.send_keys("None")

        use_case_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etUseCase"))
        )
        use_case_field.send_keys("Helps me summarize articles.")

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnSend"))
        )
        self.assertTrue(send_button.is_enabled(), "Send button should be enabled")
        send_button.click()
        
        # Try to send 2 times same form
        for i in range(2):
            send_button.click()
            print(f"Send button clicked {i+1} times")
            time.sleep(1)
        error_message_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((AppiumBy.ID, "com.example.aisurveyapp:id/submitErrorMessage"))
        )

        error_message = error_message_element.text
        self.assertTrue("You can only submit the same form once" in error_message, 
                        "Error message not displayed correctly")
        
        #Change name and usecase field and send again 
        name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etName"))
        )
        name_field.send_keys("Test2")
        use_case_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etUseCase"))
        )
        use_case_field.send_keys("I Hate AI")
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnSend"))
        )
        self.assertTrue(send_button.is_enabled(), "Send button should be enabled")
        send_button.click()


        # --- EMAIL VERIFICATION VIA IMAP ---
        email_found = self.wait_for_email(
            recipient="test.hesap458@gmail.com",
            subject_keyword="AI Survey Result",
            timeout=30
        )
        self.assertTrue(email_found, "Survey email was not received within the expected timeframe.")

    def wait_for_email(self, recipient, subject_keyword, timeout=30):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            found_names = self.check_email(recipient, subject_keyword)
            if "Test1" in found_names and "Test2" in found_names:
                return True
            time.sleep(10)
        return False

    def check_email(self, recipient, subject_keyword):
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"
        password = os.getenv("MAIL_APP_PASSWORD")
        found_names = set()

        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            mail.login(username, password)
            mail.select("inbox")
            result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()

            for mail_id in reversed(mail_ids):  # Newest to oldest
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                date_tuple = email.utils.parsedate_tz(msg["Date"])
                email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

                # Check timestamp within 5 minutes
                if datetime.now() - email_timestamp > timedelta(minutes=5):
                    continue

                body = self.extract_body_from_email(msg)
                if not body:
                    continue

                if "Name: Test1" in body:
                    found_names.add("Test1")
                if "Name: Test2" in body:
                    found_names.add("Test2")

                if found_names == {"Test1", "Test2"}:
                    break

            mail.logout()
            return found_names
        except Exception as e:
            print("Error checking email:", e)
            return set()

    def extract_body_from_email(self, msg):
        """Extracts the body content from the email."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    return body
        else:
            return msg.get_payload(decode=True).decode()

        return None

    def tearDown(self):
        if self.driver:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogout"))
            )
            logout_button.click()
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
