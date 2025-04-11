import unittest
import time
import imaplib
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
import os
from dotenv import load_dotenv
load_dotenv()
class BasicEndToEndTest(unittest.TestCase):
    def setUp(self):
        # Create and configure UiAutomator2Options for Appium 2.x
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "emulator-5554"  # or your device name
        options.platform_version = "16"        # update as needed
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

        # --- MAIN ACTIVITY PHASE --- (after login, we expect to be on MainActivity)
        name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etName"))
        )
        name_field.send_keys("Jane Doe")

        birth_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etBirthDate"))
        )
        birth_date_field.click()
        #select different date somehow here with datepicker
        done_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))
        )
        done_button.click()


        spinner = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/spinnerEducation"))
        )
        spinner.click()
        # Short wait to ensure the spinner options are loaded
        time.sleep(2)

        # Use UIAutomator to select the "Bachelor's" option
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

        bard_checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/cbBard"))
        )
        if bard_checkbox.get_attribute("checked") != "true":
            bard_checkbox.click()

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
            if self.check_email(recipient, subject_keyword):
                return True
            time.sleep(10)
        return False

    def check_email(self, recipient, subject_keyword):
        print("check email called")
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"      # UPDATE with your test email address
        #password = "CS458TestHesap"            # UPDATE with your email or app-specific password

        password = os.getenv("MAIL_APP_PASSWORD")             # UPDATE with your email or app-specific password

        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            print("1")
            try:
                print("Attempting login...")
                rv, data = mail.login(username, password)
                print(f"Login result: {rv}, {data}")
            except Exception as e:
                print("Login failed with error:", e)
            print("2")
            mail.select("INBOX")
            print("3")
            data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            print("4")
            mail_ids = data[0].split()
            mail.logout()
            return len(mail_ids) > 0
        except Exception as e:
            print("Error checking email:", e)
            return False

    def tearDown(self):
        if self.driver:
            login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogout"))
            )
            login_button.click()
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
