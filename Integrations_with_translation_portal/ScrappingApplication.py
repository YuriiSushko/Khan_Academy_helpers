import re
import time
import copy

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


# Setting filepath
chrome_driver_path = r'C:\ChromeDriver\chromedriver-win64\chromedriver.exe'

# Setting Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Name of current webpage", driver.title)


def switch_to_editor():
    driver.switch_to.frame("crowdin-editor-iframe")
    return driver.find_element(By.TAG_NAME, "body")


def switch_to_crowdin():
    driver.switch_to.default_content()
    return driver.find_element(By.TAG_NAME, "body")


def if_button_is_present(web_element):
    try:
        delete_translation_button = web_element.find_element(By.CLASS_NAME, "active_suggestion_delete_button")
        return True
    except NoSuchElementException:
        return False


def if_element_is_translated(web_element):
    try:
        element = web_element.find_element(By.CLASS_NAME, "crowdin_jipt_translated")
        return True
    except NoSuchElementException:
        return False


def if_element_is_approved(web_element):
    try:
        element = web_element.find_element(By.CLASS_NAME, "crowdin_jipt_approved")
        return True
    except NoSuchElementException:
        return False


def if_span_is_present(web_element):
    try:
        element = web_element.find_element(By.TAG_NAME, 'span')
        return True
    except NoSuchElementException:
        return False


def find_untranslated_strings():
    body_element = switch_to_crowdin()
    untranslated_elements = body_element.find_elements(By.CLASS_NAME, 'crowdin_jipt_untranslated')

    untranslated_strings = []
    body_element = switch_to_editor()
    for num in range(len(untranslated_elements)):
        source_field = body_element.find_element(By.ID, "source_phrase_container")
        source_field_text = source_field.text

        if source_field_text not in untranslated_strings:
            untranslated_strings.append(source_field_text)

        # get the next string button
        next_string_button = driver.find_element(By.ID, "next_translation")
        next_string_button.click()

    return untranslated_strings


def delete_translated_strings():
    start_time = time.time()
    body_element = switch_to_crowdin()
    translation_list = body_element.find_elements(By.TAG_NAME, 'tr')

    translated_strings = []
    for row in translation_list:
        try:
            translate_element = row.find_element(By.XPATH, './td[2]')
        except NoSuchElementException:
            print("Skipping row, no second td element found:", row.text)
            continue

        if if_element_is_translated(translate_element) or if_element_is_approved(translate_element):
            translated_strings.append(translate_element.text)

            if if_span_is_present(translate_element):
                translate_element.find_element(By.TAG_NAME, 'span').click()
            else:
                translate_element.find_element(By.CLASS_NAME, 'paragraph').click()

            switch_to_editor()

            suggestions = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "suggestion-text-container"))
            )

            if if_button_is_present(suggestions):
                # defining delete button
                delete_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "active_suggestion_delete_button"))
                )

                delete_button.click()

            switch_to_crowdin()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to delete translated strings: {elapsed_time:.2f} seconds")

    return translated_strings


delete_translated_strings()

# untranslated_strings = find_untranslated_strings()
# for element in untranslated_strings:
#     print(element)

# # Open new tab
# driver.execute_script("window.open('');")
# time.sleep(1)  # Wait for the new tab to open
#
# # Switch to the new tab
# driver.switch_to.window(driver.window_handles[-1])
# driver.get("https://www.deepl.com/translator#en/uk/separate")
#
# driver.close()
# # driver.switch_to.window(driver.window_handles[0])
