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
#End to end successful form send
class BasicEndToEndTest(unittest.TestCase):
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

        # --- MAIN ACTIVITY PHASE ---
        name_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etName"))
        )
        name_field.send_keys("Jane Doe")

        birth_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etBirthDate"))
        )
        birth_date_field.click()

        year_header = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "android:id/date_picker_header_year"))
        )
        year_header.click()

        target_year = "2015"
        max_year_scrolls = 20

        year_found = False
        for _ in range(max_year_scrolls):
            try:
                year_to_select = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().resourceId("android:id/text1").text("{target_year}")'))
                )
                year_to_select.click()
                year_found = True
                break
            except TimeoutException:
                # Scroll backward to previous years
                driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().resourceId("android:id/date_picker_year_picker")).scrollBackward()'
                )

        if not year_found:
            print("Year {target_year} not found after {max_year_scrolls} scrolls")

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
        host = "imap.gmail.com"
        username = "test.hesap458@gmail.com"
        password = os.getenv("MAIL_APP_PASSWORD")

        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            mail.login(username, password)
            mail.select("inbox")
            result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
            mail_ids = data[0].split()

            for mail_id in reversed(mail_ids):  # Start from the most recent
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                date_tuple = email.utils.parsedate_tz(msg["Date"])
                if date_tuple:
                    email_timestamp = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                    now = datetime.now()
                    if now - email_timestamp <= timedelta(minutes=5):
                        print("Email found within last 5 minutes.")
                        mail.logout()
                        return True

            mail.logout()
            return False
        except Exception as e:
            print("Error checking email:", e)
            return False

    def tearDown(self):
        if self.driver:
            logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogout"))
            )
            logout_button.click()
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
