import unittest
import time
import imaplib
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv
load_dotenv()

class BirthdateValidationTest(unittest.TestCase):
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

    def test_birthdate_in_the_future(self):
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

        # birthdate > today
        birth_date_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etBirthDate"))
        )
        birth_date_field.click()
        year_header = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "android:id/date_picker_header_year"))
        )
        year_header.click()
        future_year = "2030"
        max_year_scrolls = 20

        year_found = False
        for _ in range(max_year_scrolls):
            try:
                year_to_select = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR,
                        f'new UiSelector().resourceId("android:id/text1").text("{future_year}")'))
                )
                year_to_select.click()
                year_found = True
                print(f"✅ Year {future_year} selected")
                break
            except TimeoutException:
                driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().resourceId("android:id/date_picker_year_picker"))'
                )

        if not year_found:
            print(f"Year {future_year} not found after {max_year_scrolls} scrolls")

        done_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))
        )
        done_button.click()
        try:
            error_message_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((AppiumBy.ID, "com.example.aisurveyapp:id/birthdateErrorMessage"))
            )
            error_message_text = error_message_element.text
            print("Error message displayed: ", error_message_text)
            assert "Birthdate cannot be in the future" in error_message_text, "Error message not displayed correctly"

        except TimeoutException:
            print("Error message not displayed in time.")
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
            EC.presence_of_element_located((AppiumBy.ID, "com.example.aisurveyapp:id/btnSend"))
        )

        self.assertFalse(send_button.is_enabled(), "Send button should be disabled when birthdate is in the future.")

    def tearDown(self):
        if self.driver:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogout"))
            )
            logout_button.click()
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
