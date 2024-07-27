# executor_url = driver.command_executor._url
# session_id = driver.session_id
# -------BUBBLEFISH---------- Younger dumber cousin of Babelfish
# ------UPDATEed April 2024:
# run below in terminal to fire up a browser in debug mode pport 9222
# 1.  Google\ Chrome --remote-debugging-port=9222 --user-data-dir="~/ChromeProfile"
# 2. Then go to this page as example :
# https://sv.khanacademy.org/devadmin/translations/x5e559fd409f0ee60/xe33ac28b798af866/?lang=sv&types=all&progress=everything
# make sure there is only one active tab, or atleast the page you are interacting with should be the first tab

# This step not needed 3. then changethe width of page in developer tools for this element .1yg7hr4o from 550 to 1000 to be able to fit the chat-gpt sidebar properly. then activate that sidebar


# THEN you can run this code
# also change the size of the page
## What this code does
# DEPRC 1. gets an existing session from the JSOn file created by get_crowdin_session.py
# 2. gets the number of untranslated strings in exercise page
#  cycles through them one by one with some pauses between
#  gets the source and suggestions first and last, i.e TM and MT if available . if the TM match is above threhold val 96% including 00=100
# it uses TM otherwise it uses Crowdin Machine translation
#  it inputs the values into the edit field and presses(using javascript) the save button (automoves to next string)
# if save fails i.e new source string is same as previous it manually triggers buttonpress to next string
# Issues:
# I found it impossible to get the element id and select / click the field where to send the ALT+s send keys, so that is why action chains where used and now javscript button press i used
# theres probably some simple way I haven't figured out yet, time spent on code. maybe 15-25 hrs may 5th2021

# BELOW  FUNCTIONS DEPRECATED
##Attaches to existing Auto-browser using session_id and executor_url from session.JSON
'''def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver
## Gets saved session_if and executor_url from session.JSON
with open("session_crowdin.json", 'r') as f:
    sess = json.load(f)
print('new session IDs', sess['executor_url'],'\n', sess['session_id'] )

new_driver = attach_to_session(sess['executor_url'],sess['session_id'])
#this is for codepad.org
# #text_area = new_driver.find_element_by_id('textarea')
#scrimba.com
#text_area = new_driver.find_elements_by_css_selector('.inputarea')[0]
#print('BY CSS: ',text_area)
'''


##----> TO-DO Step through all the strings##
## --->> TO-DO fix if inputs(suggestions) are empty try/ catch?
'''
new_driver.switch_to.default_content()
#find how many untransalted strings/rows we have
# previous#  no_of_strings = len(new_driver.find_elements_by_class_name("perseus-renderer.perseus-renderer-responsive.crowdin_jipt_untranslated"))
#no_of_strings = len(new_driver.find_elements_by_class_name("perseus-renderer.perseus-renderer-responsive"))
no_of_strings = len(new_driver.find_elements_by_class_name("crowdin_jipt_untranslated")) #may work Merch 22
'''


''' TO_DO  Fix the code to auto change the styling, doesn't work right now

#Swap the width property to be able to show GPT panel 550 px-> 1000px
#style_element = body_element.find_element(By.CLASS_NAME, ('_1yg7hr4o'))
#style_element = new_driver.find_elements(By.CLASS_NAME, ('_1yg7hr4o'))
try:
    style_element = new_driver.find_elements(By.CLASS_NAME, '_1yg7hr4o')
    print("Element found:", style_element)
except NoSuchElementException:
    print("Element not found")
new_driver.execute_script("arguments.style.width = '1000px';", style_element)
input("did style get changed?")
'''