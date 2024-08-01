import time

try:
    from tqdm import tqdm
except ImportError:
    print("tqdm is not installed. Please install it using 'pip install tqdm'.")
    tqdm = None

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("colorama is not installed. Please install it using 'pip install colorama'.")
    Fore = None
    Style = None

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("selenium is not installed. Please install it using 'pip install selenium'.")

# Initialize colorama
init(autoreset=True)


class ScrappingApplication:
    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.webdriver_installed = True
        self.webdriver_error = None

        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            service = Service(self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.webdriver_installed = False
            self.webdriver_error = str(e)
            print(f"Webdriver is not installed or not configured correctly. Error: {self.webdriver_error}")

        if self.webdriver_installed:
            print("Name of current webpage:", self.driver.title)

    def switch_to_editor(self):
        self.driver.switch_to.frame("crowdin-editor-iframe")
        return self.driver.find_element(By.TAG_NAME, "body")

    def switch_to_crowdin(self):
        self.driver.switch_to.default_content()
        return self.driver.find_element(By.TAG_NAME, "body")

    def if_button_is_present(self, web_element):
        try:
            delete_translation_button = web_element.find_element(By.CLASS_NAME, "active_suggestion_delete_button")
            return True
        except NoSuchElementException:
            return False

    def if_element_is_translated(self, web_element):
        try:
            element = web_element.find_element(By.CLASS_NAME, "crowdin_jipt_translated")
            return True
        except NoSuchElementException:
            return False

    def if_element_is_approved(self, web_element):
        try:
            element = web_element.find_element(By.CLASS_NAME, "crowdin_jipt_approved")
            return True
        except NoSuchElementException:
            return False

    def if_span_is_present(self, web_element):
        try:
            element = web_element.find_element(By.TAG_NAME, 'span')
            return True
        except NoSuchElementException:
            return False

    def find_untranslated_strings(self):
        body_element = self.switch_to_crowdin()
        untranslated_elements = body_element.find_elements(By.CLASS_NAME, 'crowdin_jipt_untranslated')

        untranslated_strings = []
        body_element = self.switch_to_editor()
        for num in range(len(untranslated_elements)):
            source_field = body_element.find_element(By.ID, "source_phrase_container")
            source_field_text = source_field.text

            if source_field_text not in untranslated_strings:
                untranslated_strings.append(source_field_text)

            # get the next string button
            next_string_button = self.driver.find_element(By.ID, "next_translation")
            next_string_button.click()

        return untranslated_strings

    def delete_translated_strings(self):
        start_time = time.time()
        body_element = self.switch_to_crowdin()
        translation_list = body_element.find_elements(By.TAG_NAME, 'tr')

        progress_bar = tqdm(
            total=len(translation_list),
            desc=f"{Fore.CYAN}Deleting translated strings{Style.RESET_ALL}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            ascii=" █▓▒░"
        )

        for row in translation_list:
            try:
                translate_element = row.find_element(By.XPATH, './td[2]')
            except NoSuchElementException:
                print(f"{Fore.YELLOW}Skipping row, no second td element found:{Style.RESET_ALL} {row.text}")
                progress_bar.update(1)
                continue

            if self.if_element_is_translated(translate_element) or self.if_element_is_approved(translate_element):

                if self.if_span_is_present(translate_element):
                    translate_element.find_element(By.TAG_NAME, 'span').click()
                else:
                    translate_element.find_element(By.CLASS_NAME, 'paragraph').click()

                self.switch_to_editor()

                suggestions = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "suggestion-text-container"))
                )

                if self.if_button_is_present(suggestions):
                    # defining delete button
                    delete_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "active_suggestion_delete_button"))
                    )

                    delete_button.click()

                self.switch_to_crowdin()
            progress_bar.update(1)
        progress_bar.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to delete translated strings: {elapsed_time:.2f} seconds")

    def approve_strings(self):
        start_time = time.time()
        body_element = self.switch_to_crowdin()
        translation_list = body_element.find_elements(By.TAG_NAME, 'tr')

        progress_bar = tqdm(
            total=len(translation_list),
            desc=f"{Fore.CYAN}Approving translated strings{Style.RESET_ALL}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            ascii=" █▓▒░"
        )

        for row in translation_list:
            try:
                translate_element = row.find_element(By.XPATH, './td[2]')
            except NoSuchElementException:
                print(f"{Fore.YELLOW}Skipping row, no second td element found:{Style.RESET_ALL} {row.text}")
                progress_bar.update(1)
                continue

            if self.if_element_is_translated(translate_element):

                if self.if_span_is_present(translate_element):
                    translate_element.find_element(By.TAG_NAME, 'span').click()
                else:
                    translate_element.find_element(By.CLASS_NAME, 'paragraph').click()

                self.switch_to_editor()

                suggestions = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "suggestion-text-container"))
                )

                if self.if_button_is_present(suggestions):
                    # defining delete button
                    approve_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "approve-action"))
                    )

                    approve_button.click()

                self.switch_to_crowdin()
            progress_bar.update(1)

        progress_bar.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to approve translated strings: {elapsed_time:.2f} seconds")

    def run(self):
        print(
            f"{Fore.GREEN}{Style.BRIGHT}Hello!{Style.RESET_ALL} it's a little program that helps you do some boring job\n"
            f"{Fore.RED}* It may not do all pages, so start the code a few times *{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}{Style.BRIGHT}Options:{Style.RESET_ALL}\n"
              f"{Fore.YELLOW}To start approving all on the page, press {Fore.RED}1{Style.RESET_ALL}\n"
              f"{Fore.YELLOW}To start deleting all translations, press {Fore.RED}2{Style.RESET_ALL}\n"
              f"{Fore.YELLOW}To quit, press {Fore.RED}q{Style.RESET_ALL}\n"
              f"{Fore.YELLOW}To interrupt the program, stop it manually{Style.RESET_ALL}\n")

        user_input = ""

        while user_input != 'q':
            user_input = input()
            if user_input == '2':
                self.delete_translated_strings()
            elif user_input == '1':
                self.approve_strings()
            elif user_input == 'q':
                break
            else:
                print("Please, enter the correct command\n")
