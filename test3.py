import unittest
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv
load_dotenv()

class SendWithoutModelTest(unittest.TestCase):
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

    def test_send_without_model_selected(self):
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

        # Do not select any AI model checkboxes

        use_case_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/etUseCase"))
        )
        use_case_field.send_keys("Helps me summarize articles.")

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnSend"))
        )
        self.assertTrue(send_button.is_enabled(), "Send button should be enabled")
        send_button.click()

        error_message_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((AppiumBy.ID, "com.example.aisurveyapp:id/aiModelErrorMessage"))
        )

        error_message = error_message_element.text
        print("Error message displayed: ", error_message)
        self.assertTrue("You must select at least one AI model" in error_message, 
                        "Error message not displayed correctly")


    def tearDown(self):
        if self.driver:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.example.aisurveyapp:id/btnLogout"))
            )
            logout_button.click()
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()
