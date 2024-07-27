import re
import time
import copy

from selenium import webdriver
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


# DEBUG1
# input('Enter to continue, if Page name printed correctly:')

def insert_placeholders(raw_string='String is not correct, cannot be normalized'):
    # Normalize replace with placeholders
    placeholder_string = re.sub(r'(?<!\%[\dA-Za-z])\$(\\\$|[^\$])+\$', '§formel§', raw_string)
    placeholder_string = re.sub(r'\[\[☃\s+[a-z-]+\s*\d*\]\]', '§inmatning§', placeholder_string)
    # mt_text = re.sub(r'((!\[([^\]]+)?\]\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-(images|graphie)\.s3\.amazonaws\.com|fastly\.kastatic\.org\/ka-perseus-graphie)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,mt_text)
    # handles broken urls quite well
    # mt_text = re.sub(r'((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. )|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,mt_text)
    # handles broken urls even better

    # created this much simpler one in march 2022..maybe it is to simple sometimes, not sure?..yes can fail created below one
    # placeholder_string = re.sub(r'!\[?([^\]]+)?\]\(.*\)','§bild§' ,placeholder_string)

    # For §bild§ used the one below previously..it works but sometimes fails for some  messed up machine translations
    # placeholder_string = re.sub(r'((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om)|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,placeholder_string)
    ## this below was the live one before that also picks up the ![] that may contain text
    # placeholder_string = re.sub(r'((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om|come.s3. .*)|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,placeholder_string)
    placeholder_string = re.sub(
        r'((\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om|come.s3. .*)|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg|html|htm))?\)?)',
        '§bild§', placeholder_string)
    # this regex also captures missing '/' before all the numbers in url, somoetimes found in deepl Translations
    # --regex-> ((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om)|fastly\.kastatic\.org\/ka-perseus-graphie|)(\/|\d)[0-9a-f]+(\.(svg|png|jpg))?\)?)

    return placeholder_string


def remove_placeholders(target, src_formulae1, src_inputs1, src_images1):
    # replaces placeholders with source string values
    regex_hit_list = copy.deepcopy(src_formulae1)  # src_formulae
    while "§formel§" in target:
        # print('From Function Regex_hit_List: \n', regex_hit_list)
        next_formula = regex_hit_list.pop(0)  # Next "source formula"
        target = target.replace("§formel§", next_formula, 1)

    regex_hit_list = copy.deepcopy(src_inputs1)  # src_inputs
    while "§inmatning§" in target:
        next_input = regex_hit_list.pop(0)  # Next "source input"
        target = target.replace("§inmatning§", next_input, 1)

    regex_hit_list = copy.deepcopy(src_images1)  # src_images
    while "§bild§" in target:
        next_image = regex_hit_list.pop(0)[0]  # Next "source image"
        target = target.replace("§bild§", next_image, 1)
    return target


# Navigate to a specific element (e.g., the body tag)
body_element = driver.find_element(By.TAG_NAME, "body")

# Find all elements with the class name "crowdin_jipt_untranslated" within the body
untranslated_elements = body_element.find_elements(By.CLASS_NAME, "crowdin_jipt_untranslated")

# Get the number of untranslated strings
no_of_strings = len(untranslated_elements)
# DEBUG2
print('Number of strings on page:', no_of_strings)
# input('Enter to continue, if number of strings correct:')

# run code no_of_strings times
# print('Driver swapped + ',no_of_strings)
source_previous = '--previous--'
# switch to the Iframe with editor and MT suggestions
driver.switch_to.frame("crowdin-editor-iframe")
# Navigate to a specific element (e.g., the body tag)
body_element = driver.find_element(By.TAG_NAME, "body")

# print('switched frame')
for num in range(no_of_strings):
    try:
        # get the various elements used
        # get the source string ( to check if you are stuck and force move to next string)
        # Find the source phrase container within the body
        source_field = body_element.find_element(By.ID, "source_phrase_container")
        # Get the text from the source field
        source_field_text = source_field.text
        print(source_field_text)

        # OLD    source_field = new_driver.find_element_by_id('source_phrase_container')
        # OLD    source_field_text =source_field.text
        # print('get text from source',source_field_text ) #works to here
        # check if stuck previous == current source
        if source_field_text == source_previous:
            # get the next string button
            next_string_button = driver.find_element(By.ID, "next_translation")
            # OLD next_string_button = new_driver.find_element_by_id('next_translation')
            # then press button to move to next string, otherwise continue
            driver.execute_script("arguments[0].click();", next_string_button)
            print('pressed NEXT BUTTON!!!')
            # new_driver.switch_to.default_content()
            time.sleep(3)
            continue
        # The edit field where you enter your translation
        text_field = driver.find_element(By.ID, "translation")

        # The save button that saves your suggested translation
        save_button = driver.find_element(By.ID, "suggest_translation")
        # the edit field that we enter our text into
        # OLD text_field = new_driver.find_element_by_id('translation')

        # the edit field that holds the text shown? why these two are different, and how?? atleast it works...
        # OLD save_button = new_driver.find_element_by_id('suggest_translation')

        # Find the input field with the specified class name
        edit_field = body_element.find_element(By.CLASS_NAME, "input-block-level.ui-autocomplete-input")
        # edit_field= new_driver.find_element_by_class_name("hwt-highlights.hwt-content")
        # OLD edit_field= new_driver.find_element_by_class_name("input-block-level.ui-autocomplete-input")
        # time.sleep(2)
        # find all the suggestions and scores
        # TM and Machine translation MT is the last one [-1] and first if no TMs exist[0]
        # Find all elements with the class name "suggestion_tm_translation"
        for _ in range(3):
            suggestions = body_element.find_elements(By.CLASS_NAME, "suggestion_tm_translation")
            # Get the first suggestion (if available)
            if suggestions:
                first_suggestion = suggestions[0]
                # Now you can interact with the first suggestion as needed
                break
            else:
                # suggestions = 'NOTHING FOUND HERE!!!'
                print("No suggestions found. Retrying in 2 seconds...")
                time.sleep(2)
        # Get the contents of the different tm-contents shwoing the differences found

        tm_suggestion_diffs = body_element.find_elements(By.CSS_SELECTOR, ".suggestion_tm_source.mt-1")
        if tm_suggestion_diffs:
            # print(tm_suggestion_diff)
            ## reinstate
            first_diff = tm_suggestion_diffs[0]
            print('number of diffs:', len(tm_suggestion_diffs), 'Number of suggestions:', len(suggestions))
            print(first_diff.text)
            print(tm_suggestion_diffs[0].text)
            print('\nsource = "' + source_field_text + '"')
            print(source_field.get_attribute('innerHTML'))

            print('suggestion = "' + suggestions[0].get_attribute('innerHTML') + '"')
            print('correction =  "' + tm_suggestion_diffs[0].get_attribute('innerHTML') + '"')

        # input('Stop code.....')

        # suggestions = body_element.find_element(By.CLASS_NAME,'suggestion-text-container align-items-center')
        # 1st suggestions = body_element.find_element(By.CLASS_NAME,'suggestion_tm_translation')
        # OLD suggestions = new_driver.find_elements_by_class_name('suggestion_tm_translation')
        # the scores of the TM suggestions 'e.g '...96% match'

        # Find all elements with scores and grab the first one
        scores = body_element.find_elements(By.CLASS_NAME, 'suggestion_relevant')
        # Get the first suggestion (if available)
        if scores:
            first_score = scores[0]
            # Now you can interact with the first suggestion as needed
        else:
            # scores = "62→77% match"
            print("No Scores found.")

        # OLD scores = new_driver.find_elements_by_class_name('suggestion_relevant')
        # set the value to compare with at top of loop
        source_previous = source_field_text

        print('suggestion_list-len', len(suggestions))  # ,'edit_fields-len',len(edit_field))
        # DEBUG3
        # print('Suggestions.text', suggestions, suggestions[0].text)# suggestions.text)#suggestions[0].text)
        # Print the text content of each suggestion
        # for suggestion in suggestions:
        #    print("Suggestion:", suggestion.text)
        # input("DEBUG3:----Enter to continue if you get a bunch of values...")

        ###-----------Set-up for LLM interaction-----###
        ##  TO_DO
        ## create a function out of it

        # Find all elements with the specified class name
        suggestion_elements = body_element.find_elements(By.CLASS_NAME, "suggestion")

        # Filter elements based on the desired languages ('de','es','fr')
        desired_languages = ['de', 'es', 'fr']
        filtered_suggestions = [elem for elem in suggestion_elements if elem.get_attribute("lang") in desired_languages]
        print(filtered_suggestions)
        # Extract the text from the filtered suggestions
        for suggestion in filtered_suggestions:
            suggestion_text = suggestion.text
            print("Suggestion ({}):".format(suggestion.get_attribute("lang")))
            print("Suggestion_text:", suggestion_text)
        # input("Stop and check it works as expected")

        # set vars incase they are missing...may crash anyway, not sure
        score = 1
        mt_text, tm_text, final_text = '', '', ''
        # if no MT suggestion then use first TM suggestion (instead of last) ( maybe use Deepl MT instead as backup)

        #####TO-Do add catch if suggestions is completely empty

        if len(suggestions) == len(scores):
            score = 98
            print('No MT suggestion , using first TM suggestion instead')
        try:
            mt_text = suggestions[-1].text
            tm_text = suggestions[0].text
            percent_position = scores[0].text.find('%')
            score = scores[0].text[percent_position - 2:percent_position]
        except Exception as err:
            print("Error {}".format(err))

        print('Source text: \n', source_field_text)
        print('Machine Translation text: \n', mt_text)
        print('full TM-text1: \n', tm_text)
        print('percentage: ', score, '# of Strings onpage:', no_of_strings)
        print('current text in translation:\n', edit_field.text)

        # suggestions[-1].click()
        edit_field.clear()
        # time.sleep(1)
        text_field.clear()
        time.sleep(1)
        # input("Enter to continue if test was cleared...")

        # extract formulas and replace with English formula(hopefully)
        # get formulas from source string
        src_formulae = re.findall(r'(?<!\%[\dA-Za-z])\$(\\\$|[^\$])+\$', source_field_text)
        src_inputs = re.findall(r'\[\[☃\s+[a-z-]+\s*\d*\]\]', source_field_text)

        # src_images = re.findall(r'((!\[([^\]]+)?\]\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-(images|graphie)\.s3\.amazonaws\.com|fastly\.kastatic\.org\/ka-perseus-graphie)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)',source_field_text)
        ## this below was the live one before that also picks up the ![] that may contain text
        # src_images = re.findall(r'((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. )|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)',source_field_text)

        src_images = re.findall(
            r'((\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om|come.s3. .*)|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg|html|htm))?\)?)',
            source_field_text)
        if len(src_images) > 1:
            temp_list = []
            for group in src_images:
                temp_list.append(group[0])
            src_images = temp_list

        # the below captures also broken  MT !|texts missing end ']' but results in lost translation of caption? how to handle?
        # src_images = re.findall(r'((!\[([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-(images|graphie)\.s3\.amazonaws\.com|fastly\.kastatic\.org\/ka-perseus-graphie)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)',source_field_text)

        # replace latex wtc with §formel§, §bild§,§inmatning§ text in target string
        # mt_text = re.sub(r'(\$(\\\$|[^\$])+\$)','§formel§', mt_text)
        src_formulae = re.findall(r'(\$(\\\$|[^\$])+\$)', source_field_text)
        # create new list, using first element in each tuple, since current regex creates multiple capture groups creating nested list of tuples
        if len(src_formulae) > 0:
            temp_list = []
            for group in src_formulae:
                temp_list.append(group[0])
            src_formulae = temp_list

        if int(score) > 99 or score == '00':
            tm_text = tm_text.replace(': -:', ':-:')
            tm_text = tm_text.replace('Grafie', 'graphie')
            final_text = tm_text
            # text_field.send_keys(tm_text)
            # text_field.innerText = tm_text
            print('score:', score, '% ----> Using Translation Memory Text')
        else:
            # text_field.send_keys("holiday on mars\n Reg rules!")
            print('score:', score, '% ----> Using Machine Translation Text')
            # mt_text = insert_placeholders(mt_text)

            # GET THE CROWDIN TRANSLATE VALUE FROM CHAT GPT

            ## TO-DO. fix location of button expand pane, to aviod collapsing

            panel_button = driver.find_element(By.XPATH,
                                                   '//*[@id="translation_text_container"]/div[1]/div[1]/button[3]')
            panel_button.click()
            time.sleep(1)
            # input('Did GPT / translate show?    ')
            # panel_button.click()
            # input("did it close it again")
            # driver = webdriver.Chrome()
            # driver.get('URL_OF_PAGE')
            # Switch to the iframe containing the button element
            # input("about to switch frames")
            iframe = driver.find_element(By.XPATH, '//iframe')
            driver.switch_to.frame(iframe)

            # Locate the button element and click it
            button = driver.find_element(By.XPATH, '//button[text()="Translate"]')
            button.click()
            time.sleep(0.5)


            # Define a custom condition to check for non-empty text in the element
            class element_has_non_empty_text(object):
                def __init__(self, locator):
                    self.locator = locator

                def __call__(self, driver):
                    element = WebDriverWait(driver, 0.5).until(
                        EC.presence_of_element_located(self.locator))
                    if element.text:
                        return element
                    else:
                        return False


            # Define a custom condition to check that the element's text is not '...'
            class element_has_specific_text(object):
                def __init__(self, locator, text):
                    self.locator = locator
                    self.text = text

                def __call__(self, driver):
                    element = WebDriverWait(driver, 0.5).until(
                        EC.presence_of_element_located(self.locator))
                    if element.text != self.text:
                        return element
                    else:
                        return False


            # Use WebDriverWait with the custom condition
            # info_element = WebDriverWait(new_driver, 10).until(
            #    element_has_non_empty_text((By.XPATH, '//div[@class="sc-bZQynM XYICJ rsc-ts-bubble"]/div'))
            # )
            # Use WebDriverWait with the custom condition
            info_element = WebDriverWait(driver, 20).until(
                element_has_specific_text((By.XPATH, '//div[@class="sc-bZQynM XYICJ rsc-ts-bubble"]/div'), '...')
            )

            # Wait for the information to be displayed
            # info_element = WebDriverWait(new_driver, 10).until(
            #    EC.presence_of_element_located((By.XPATH, '//div[@class="sc-bZQynM XYICJ rsc-ts-bubble"]/div'))
            # )

            '''# Wait for the information to be displayed
            info_element = WebDriverWait(new_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "sc-bZQynM") and contains(@class, "XYICJ") and contains(@class, "rsc-ts-bubble")]/div'))
            )'''
            # Output the HTML of the located element
            # element_html = info_element.get_attribute("outerHTML")
            # print(element_html)
            # Extract the text from the information element
            gpt_text = info_element.text
            print(gpt_text)
            # input("through the gpt stuff- output gpt_text?")

            # Create an ActionChains object passing the driver instance
            actions = ActionChains(driver)

            # Move to the element located, then move by the offset you want, then click
            actions.move_to_element(info_element).move_by_offset(-250, 20).click().perform()
            # input("did panel get closed again?")
            # Switch back to the default content
            driver.switch_to.default_content()
            # switch to the Iframe with editor and MT suggestions
            driver.switch_to.frame("crowdin-editor-iframe")
            # input('GPT_Step: Check if you got the GPT suggestions string')
            """ mt_text = re.sub(r'(?<!\%[\dA-Za-z])\$(\\\$|[^\$])+\$','§formel§', mt_text)
            mt_text = re.sub(r'\[\[☃\s+[a-z-]+\s*\d*\]\]','§inmatning§',mt_text)
            #mt_text = re.sub(r'((!\[([^\]]+)?\]\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-(images|graphie)\.s3\.amazonaws\.com|fastly\.kastatic\.org\/ka-perseus-graphie)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,mt_text)
            mt_text = re.sub(r'((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om)|fastly\.kastatic\.org\/ka-perseus-graphie|)\/[0-9a-f]+(\.(svg|png|jpg))?\)?)','§bild§' ,mt_text)
            # this regex also cpatures missing / before all the numbers in url, somoetimes found in deepl Translations
            #--regex-> ((!\[?([^\]]+)?\]?\s*?\()?\s*(http|https|web\+graphie):\/\/(ka-perseus-:\/\/)?(ka-perseus-(images|graphie)\.s3\.amazonaws\.(com|come. 3. ?|come.3.<unk> aws. om)|fastly\.kastatic\.org\/ka-perseus-graphie|)(\/|\d)[0-9a-f]+(\.(svg|png|jpg))?\)?) """

            # replace §formel§ etc placeholders with original text from source
            # Commented out below for GPT work 2
            # mt_text = remove_placeholders(mt_text, src_formulae, src_inputs, src_images)
            # for GPT set mt_text = gpt_text
            mt_text = gpt_text
            """ while "§formel§" in mt_text:
                next_formula = src_formulae.pop(0) # Next "source formula"
                mt_text = mt_text.replace("§formel§", next_formula, 1)
            while "§inmatning§" in mt_text:
                next_input = src_inputs.pop(0) # Next "source input"
                mt_text = mt_text.replace("§inmatning§", next_input, 1)
            while "§bild§" in mt_text:
                next_image = src_images.pop(0)[0] # Next "source image"
                mt_text = mt_text.replace("§bild§", next_image, 1) """

            print('New MT-String: ', mt_text)
            # ---->> To-do cleanup the MT string
            # <unk> = | , missing * = **
            mt_text = mt_text.replace('<unk>', '|').replace(': -:', ':-:').replace('Grafie', 'graphie').replace(' *\\n',
                                                                                                                '**\n').replace(
                "$:\n-", "$:\n\n-")  # .replace("\\\\\\\n","\\\\    \\n")#.replace("\\\\\\\\\\\\\\\\", "\\\\\\\\\\\\\\")
            # print('New MT-String after first replace: ', mt_text)
            mt_text = mt_text.replace("\\\\\\n", "\\\\ \\n ")  # .replace("\\\\\\\\\\\\\\\\", "\\\\\\\\\\\\\\")
            # print('New MT-String after Backslash replace: ', mt_text)
            # Do same replace on source string
            mod_source_field_text = source_field_text.replace("\\\\\\n",
                                                              "\\\\ \\n ")  # .replace("\\\\\\\\\\\\\\\\", "\\\\\\\\\\\\\\")
            # print('New source-String after Backslash replace: ', mod_source_field_text)
            # cleanup URL's ??
            # missing ,\'letter' = ,\\'letter' - can't solve \t intepreted as [tab]
            # mt_text = mt_text.replace('\\\\,\d','\\\\,\\\\d').replace('\\\\,\c','\\\\,\\\\c').replace('\\\\, \c','\\\\,\\\\c').replace('\\\\, \d','\\\\,\\\\d') #replace('\, \\',',\\').

            # mt_text = mt_text.replace('\\,d','\\,\d').replace('\\,c','\\,\c').replace('\\, c','\\,\c').replace('\\, d','\\,\d')
            # mt_text = mt_text.replace('\\\\,\\t','\\\\,\\\\t').replace('\\ \\t ext', '\\\\text').replace('. \\o', '.\\\\o')
            # mt_text = mt_text.replace('{, 0','{,}0').replace('{, 5','{,}5')
            mt_text = re.sub(r"({, *)(\d)", "{,}\g<2>", mt_text)
            # Regex to find digits followed by '\%' and replace them with '\\%'
            mt_text = re.sub(r'(\d)\\%', r'\1\\\\%', mt_text)
            # Regex to replace '$\stackrel{\div' with '$\\stackrel{\\div'
            # Ensuring double backslashes in the output
            print('Before final FIND REPLACE: ', mt_text)
            # mt_text = re.sub(r'\$\\stackrel\{\\div', r'$\\\\stackrel{\\\\div', mt_text)
            # mt_text = re.sub(r'\}\\rightarrow', r'}\\\\rightarrow', mt_text)
            # mt_text = re.sub(r'\}\\times', r'$\\\\stackrel{\\\\div', mt_text)

            # Code to correct backslashes in text
            from collections import Counter


            def analyze_backslashes(text):
                # Find all sequences of backslashes
                sequences = re.findall(r'\\+', text)
                # Use Counter to count occurrences of each sequence length
                sequence_lengths = Counter(len(seq) for seq in sequences)
                if not sequence_lengths:
                    return 0, 0, []  # No sequences found
                # Find the maximum sequence length and count its occurrences
                max_length = max(sequence_lengths.keys())
                max_count = sequence_lengths[max_length]
                print(max_length, max_count, sequences)
                return max_length, max_count, sequences


            ### Step 2: Function to Adjust the Translated Text Based on Analysis
            def adjust_backslashes(original, translated):
                orig_max_length, orig_max_count, _ = analyze_backslashes(original)
                trans_max_length, trans_max_count, trans_sequences = analyze_backslashes(translated)
                print(orig_max_length, '\n', trans_max_length)

                # If the maximum backslash sequence length differs
                if orig_max_length != trans_max_length and trans_max_length > 2:

                    # Check if orig_max_length is even and greater than 4
                    if orig_max_length % 2 == 0 and orig_max_length > 4:
                        print("Original max length is even and greater than 2, no adjustment needed.")
                    else:
                        print("Adjusting original max length...")
                        # orig_max_length -= 1  # Reduce the value by 1
                    # Regular expression to target the translated maximum sequences

                    trans_max_sequence = '\\' * trans_max_length
                    correct_sequence = '\\' * orig_max_length
                    print(trans_max_sequence, correct_sequence)
                    # Replace occurrences of the translated max sequence with the original max sequence
                    adjusted_text = translated.replace(trans_max_sequence, correct_sequence)
                    return adjusted_text
                return translated


            # Example usage:
            # original_text = r"Let's see if the third expression is equivalent to $3x+3(x+y)$.\n\n$\n\\begin{align}\n\\greenD{3xy}  &\\stackrel{?}{=} 3x+3(x+y)   \\\\\\\\\n\\greenD{3\\times x\\times y}  &\\stackrel{?}{=} 3x+3(x+y)   \\\\\\\\\n\\greenD{3\\times x\\times y}  &\\stackrel{?}{=} 3x+3x+3y   \\\\\\\\\n\\greenD{3\\times x\\times y}    &\\neq3(x+x+y) \n \\end{align}$"
            # translated_text = r"Давайте подивимось, чи третій вираз еквівалентний до $3x+3(x+y)$.\n\n$\\begin{align}\n\\greenD{3xy}  &\\stackrel{?}{=} 3x+3(x+y)   \\\n\\greenD{3\\times x\\times y}  &\\stackrel{?}{=} 3x+3(x+y)   \\\n\\greenD{3\\times x\\times y}  &\\stackrel{?}{=} 3x+3x+3y   \\\n\\greenD{3\\times x\\times y}    &\\neq3(x+x+y) \n\\end{align}$"

            # Adjust the translated text
            adjusted_text = adjust_backslashes(mod_source_field_text, mt_text)

            print("Adjusted Text:")
            print(adjusted_text)
            mt_text = adjusted_text

            # Version 1 of multi regex replace
            """         def ensure_proper_latex_escaping(text):
                # List of known LaTeX command words that should be preceded by double backslashes
                latex_commands = ['times', 'rightarrow', 'div', 'stackrel', 'frac', 'alpha', 'beta', 'sum', 'int', 'begin', 'end', 'bar', 'tilde']

                # Detect commands that are present in the text
                present_commands = {command for command in latex_commands if '\\' + command in text}

                # Apply regex replacements only for detected commands
                for command in present_commands:
                    # Build the regex pattern dynamically for each command
                    # This regex matches a single backslash (not preceded by another backslash) followed by the command word
                    pattern = r'(?<!\\)\\(' + command + ')'
                    # Replacement should be a double backslash followed by the command word
                    replacement = r'\\\\\1'
                    text = re.sub(pattern, replacement, text)

                return text """


            # Version 2 Regex replacing any single \ followed by letter, with double backslash
            def correct_latex_escapes(text):
                # Temporarily replace escaped dollar signs to avoid confusion with LaTeX delimiters
                text = text.replace(r'\$', r'\¢')

                # This regex matches a single backslash followed by any letter, where the backslash is not preceded by another backslash
                # pattern = r'(?<!\\)\\([a-zA-Z])'
                # Regex matches a single backslash followed by any letter except 'n' as a word boundary ( to capture \n but not \neq), unless where the backslash is not preceded by another backslash
                # and it's inside a non-greedy $...$ block. It excludes matching \n by using a negative lookahead.
                pattern = r'(?<!\\)\\(?!n\b)([a-zA-Z])'

                # Function to replace matched patterns within $...$ blocks
                def replace_func(match):
                    return r'\\' + match.group(1)

                # Regex to find all non-greedy $...$ blocks and apply the replacement function within those blocks only
                corrected_text = re.sub(r'\$[^$]*?\$', lambda m: re.sub(pattern, replace_func, m.group(0)), text)
                print(corrected_text)
                # Restore the escaped dollar signs
                corrected_text = corrected_text.replace(r'\¢', r'\$')

                return corrected_text


            # Sample text with LaTeX formatting issues and some correct ones
            # mt_text = "Some text: \\times and here's an arrow \\\\rightarrow, also an integral \\int and a fraction \\frac."

            # Correcting the LaTeX formatting
            mt_text = correct_latex_escapes(mt_text)


            # FIX  ERROR IN dropped ** bold face
            def correct_dropped_bold_formatting(source, translation):
                # Count bold markers in source and translation
                source_bold_count = len(re.findall(r'\*\*', source))
                translation_bold_count = len(re.findall(r'\*\*', translation))

                print(f"Source Bold Count: {source_bold_count}, Translation Bold Count: {translation_bold_count}")

                # Function to replace single asterisks with double if the bold counts mismatch
                if source_bold_count != translation_bold_count:
                    # Find lone asterisks
                    lone_asterisks = re.findall(r'(?<!\*)\*(?!\*)', translation)
                    print(f"Lone Asterisks found: {len(lone_asterisks)}")

                    if lone_asterisks:
                        # Replace lone asterisks with double asterisks
                        translation = re.sub(r'(?<!\*)\*(?!\*)', '**', translation)

                return translation


            # Example usage
            # source = 'To graph the inequality $d>5\\dfrac{1}{2}$, we first **draw a circle at  $5\\dfrac{1}{2}$**.  This circle divides the number line into two sections: one that contains solutions to the inequality and one that does not.  \n\nThe solution does not include the point $d=5\\dfrac{1}{2}$, so the circle at $5\\dfrac{1}{2}$ is **not filled in**.\n\nBecause the solution to the inequality says that $d>5\\dfrac{1}{2}$, this means that solutions are numbers to the **right** of $5\\dfrac{1}{2}$.'
            # translation = 'Щоб зобразити нерівність $d>5\\dfrac{1}{2}$, спочатку **малюємо коло в точці $5\\dfrac{1}{2}$**. Це коло поділяє числову пряму на дві частини: одна частина містить розв' + "'язки нерівності, а друга частина не містить. \n\nМножина розв'язків не включає точку $d=5\\dfrac{1}{2}$, тому коло в точці $5\\dfrac{1}{2}$ **не заповнюємо**.\n\nОскільки розв'язки нерівності такі: $d>5\\dfrac{1}{2}$, це означає, що розв'язки знаходяться *праворуч* від $5\\dfrac{1}{2}'.$"

            corrected_translation = correct_dropped_bold_formatting(source_field_text, mt_text)
            print("Corrected Translation:")
            print(corrected_translation)

            # FIX DOLLAR and freefloating numbers AMOUNTS
            '''
            def correct_money_notation(text):
                # Regex to find dollar amounts that are not properly formatted
                # This finds unescaped dollar signs followed by digits, possibly with a decimal point
                pattern = r'(?<!\\)(?<!\$)\$(\d+\.?\d*)' #previous
                pattern = r'(?<!\\)(?<!\$)\$(\d+\.?\d*)(?!\$)'


                # Function to replace the found patterns
                def replace_func(match):
                    # Encapsulates with LaTeX block boundaries and escapes the dollar
                    return r'$\\${}$'.format(match.group(1))

                # Replace in the entire text
                corrected_text = re.sub(pattern, replace_func, text)

                return corrected_text
            '''

            # BELOW ALMOST WORKS well, has some edgecase issues I think
            '''
            def correct_numeric_notation(text):
                # Regex to find numbers that are not enclosed in LaTeX dollar signs
                # This finds numbers that may be preceded by a dollar sign and are not already in a LaTeX block
                pattern = r'(?<!\$)(\$)?(\d+\.?\d*)(?!\$)'
                pattern = r'(?<!\$)(\$)?(\d+(?:\.\d+)?)(?![^\s]*\$)'

                # Function to replace the found patterns
                def replace_func(match):
                    # Check if there's a dollar sign before the number
                    dollar_prefix = match.group(1)
                    number = match.group(2)
                    # Encapsulate with LaTeX block boundaries
                    if dollar_prefix:
                        # If there was a dollar sign, it's money and should be escaped
                        return r'$\\${}$'.format(number)
                    else:
                        # If no dollar sign, just encase the number in dollar signs
                        return r'${}$'.format(number)

                # Replace in the entire text
                corrected_text = re.sub(pattern, replace_func, text)

                return corrected_text

            # Example usage
            text = r"This is incorrect $4.50 and should be formatted, but this is correct $\\$4.50$."
            corrected_text = correct_numeric_notation(fr'{mt_text}')
            print('corrected text:',corrected_text)
            mt_text = corrected_text
            '''
            # print('After final FIND REPLACE: ',mt_text, corrected_text)
            print('After final FIND REPLACE: ', mt_text)
            # Final Clean up:
            # clean up occurences of \\n if they aren't in source_code
            if '\\\\n' in mt_text and '\\\\n' not in source_field_text:
                mt_text = mt_text.replace('\\\\n', '\\n')
            print('After Final cleanup!:', mt_text)
            final_text = mt_text

        print('----Find & Replace Done----')

        # send text - This is where all the time is spent!!! how get faster?
        # ? insert final_text direct instead of sendkeys ?Solution : use javascript magic to insert text into editbox as below...
        # text_field.send_keys(final_text)
        # text_field.innerText = mt_text
        # test of execute script
        # new_driver.execute_script("document.getElementById('translation').setAttribute('value', '" + final_text +"')")
        # new_driver.execute_script("arguments[0].setAttribute('value', '" + final_text +"');", text_field)
        # new_driver.execute_script("document.getElementById('translation').value=' "+final_text+" ' ")
        # hello =rf'hello goodbye hello goodbyehello {hello0} goodbyehello goodbye \\n hello goodbyehello goodbyehello goodbye'
        if "This model's maximum context length" in final_text:
            print('GPT Model Overloaded Context window ! Moving to next string')
            time.sleep(1)
            pass
        else:
            # only way I could get the string with escape characters to be accepted by js function below was to first encode and then decode..guessing there is some issue with escape chars
            hello = final_text.encode('unicode_escape').decode()
            print('Hello: ', hello)
            try:
                tester = driver.execute_script(
                    "document.getElementById('translation').value = '" + hello + "';")  # .value=' hello ' ")
            except:
                print('Something went wrong with javascript typing - Using sendkeys')
                text_field.send_keys(final_text)
                tester = None
            # need to send some keys to trigger data to be input so insert an x and then backspace it => no change
            text_field.send_keys('x', Keys.BACKSPACE)
            print('keys done sending')
            print('Tester val: ', tester)
            # time.sleep(20)
            print('Save text tags...')

            # find text tags
            res = re.findall(r'text\{.*?\}', final_text)
            # append the unique ones to file
            with open("text_tags.txt", 'a') as f:
                for tag in set(res):
                    f.write(f"\n{tag}")
            print('Done Save text tags...')
            # input('Stopping code')
            time.sleep(1)
            # new_driver.implicitly_wait(5)
            driver.execute_script("arguments[0].click();", save_button)
            # save_button.click()
            # actions = ActionChains(new_driver).key_down(Keys.ALT).send_keys("x").key_up(Keys.ALT).perform()
            time.sleep(1.5)
            # input('Keep forging on...: press button')
        # exception handling to Increase resilience andstop code from crashing, when errors occur.
    except ZeroDivisionError:
        print("Attempted to divide by zero. Skipping To next string.")
    except TypeError:
        print("Type error encountered with item:", "Skipping to next string.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}. Skipping to next string.")
    else:
        # Optional: code to execute if the try block does NOT raise an exception
        print("Operation successful for:")
    finally:
        # Optional: code that is executed no matter what, often used for cleanup
        print("Iteration complete.")
# switch back to default content
driver.switch_to.default_content()
'''
webdriver.executeScript("document.getElementById('elementID').setAttribute('value', 'new value for element')");
'''

# time.sleep(5)
# save_button.click()
# actions = ActionChains(new_driver).key_down(Keys.ALT).send_keys("x").key_up(Keys.ALT).perform()

# time.sleep(1)
# actions = ActionChains(new_driver).send_keys("holiday on mars\n Reg rules!").perform()


# actions = ActionChains(new_driver).key_down(Keys.ALT).send_keys("z").key_up(Keys.ALT).perform()
# #actions.send_keys(Keys.CONTROL + 'z')
# #actions.perform()
# ##edit_field[0].send_keys(Keys.ALT + 'z')


""" # below version works nominally
for string in strings:
#     #print(div.text)
    print('ElementSize:',string.size, string.location['y'], string.location['x'], string.location)#, string.text)
    time.sleep(2)
    #string.location_once_scrolled_into_view
    #print(string.position)
    #new_driver.execute_script("arguments[0].scrollIntoView();", string)
    #string.click()
    #time.sleep(3)

    desired_y = (string.size['height'] / 2) + string.location['y']
    window_h = new_driver.execute_script('return window.innerHeight')
    window_y = new_driver.execute_script('return window.pageYOffset')
    current_y = (window_h / 2) + window_y
    scroll_y_by = desired_y - current_y
    print('Desired_Y:',desired_y, 'windowInnerH:',window_h,'PageYOffset',window_y, 'CurrentY:',current_y)
    print('Scrolling by:', scroll_y_by)
    time.sleep(2)
    if desired_y < current_y - 10:
        print('No Scroll')
    else:
        new_driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)"""