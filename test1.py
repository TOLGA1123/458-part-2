import unittest
import time
import imaplib
import email
from appium import webdriver
from appium.options.android import UiAutomator2Options

class BasicEndToEndTest(unittest.TestCase):
    def setUp(self):
        # Create and configure UiAutomator2Options for Appium 2.x
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Emulator"  # or your device name
        options.platform_version = "13"            # update as needed
        options.app_package = "com.example.aisurveyapp"
        options.app_activity = ".LoginActivity"
        options.automation_name = "UiAutomator2"
        options.no_reset = True

        # Note the updated URL - no "/wd/hub" since Appium 2.x uses the root endpoint.
        self.driver = webdriver.Remote("http://localhost:4723", options=options)
        self.driver.implicitly_wait(10)

    def test_basic_end_to_end_submission(self):
        driver = self.driver

        # --- LOGIN PHASE ---
        email_field = driver.find_element("id", "com.example.aisurveyapp:id/etUserInput")
        email_field.send_keys("test@example.com")

        password_field = driver.find_element("id", "com.example.aisurveyapp:id/etPassword")
        password_field.send_keys("password123")

        login_button = driver.find_element("id", "com.example.aisurveyapp:id/btnLogin")
        login_button.click()
        time.sleep(3)

        # --- SURVEY FORM PHASE ---
        name_field = driver.find_element("id", "com.example.aisurveyapp:id/etName")
        name_field.send_keys("Jane Doe")

        birth_date_field = driver.find_element("id", "com.example.aisurveyapp:id/etBirthDate")
        birth_date_field.click()
        birth_date_field.send_keys("1998-06-15")
        driver.back()

        spinner = driver.find_element("id", "com.example.aisurveyapp:id/spinnerEducation")
        spinner.click()
        bachelor_option = driver.find_element_by_xpath("//android.widget.TextView[@text=\"Bachelor's\"]")
        bachelor_option.click()

        city_field = driver.find_element("id", "com.example.aisurveyapp:id/etCity")
        city_field.send_keys("Ankara")

        female_radio = driver.find_element_by_xpath("//android.widget.RadioButton[@text='Female']")
        female_radio.click()

        chatgpt_checkbox = driver.find_element("id", "com.example.aisurveyapp:id/cbChatGPT")
        if chatgpt_checkbox.get_attribute("checked") != "true":
            chatgpt_checkbox.click()

        bard_checkbox = driver.find_element("id", "com.example.aisurveyapp:id/cbBard")
        if bard_checkbox.get_attribute("checked") != "true":
            bard_checkbox.click()

        cons_field = driver.find_element("id", "com.example.aisurveyapp:id/etCons")
        cons_field.send_keys("None")

        use_case_field = driver.find_element("id", "com.example.aisurveyapp:id/etUseCase")
        use_case_field.send_keys("Helps me summarize articles.")

        send_button = driver.find_element("id", "com.example.aisurveyapp:id/btnSend")
        self.assertTrue(send_button.is_enabled(), "Send button should be enabled")
        send_button.click()

        # --- EMAIL VERIFICATION VIA IMAP ---
        email_found = self.wait_for_email(
            recipient="test.hesap458@gmail.com",
            subject_keyword="AI‑Survey Result",
            timeout=30
        )
        self.assertTrue(email_found, "Survey email was not received within the expected timeframe.")

    def wait_for_email(self, recipient, subject_keyword, timeout=30):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.check_email(recipient, subject_keyword):
                return True
            time.sleep(5)
        return False

    def check_email(self, recipient, subject_keyword):
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"      # UPDATE with your test email address
        password = "CS458TestHesap"         # UPDATE with your email or app-specific password

        try:
            mail = imaplib.IMAP4_SSL(host)
            mail.login(username, password)
            mail.select("inbox")
            result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()
            mail.logout()
            return len(mail_ids) > 0
        except Exception as e:
            print("Error checking email:", e)
            return False

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
