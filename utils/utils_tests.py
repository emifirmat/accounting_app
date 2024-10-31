""" Custom functions for testing files"""
import time
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from erp.models import PaymentTerm, PaymentMethod


"""DB custom functions"""
def create_extra_pay_terms():
    """Create additional payment terms for testing."""
    PaymentTerm.objects.bulk_create([
        PaymentTerm(pay_term="60"),
        PaymentTerm(pay_term="90"),
        PaymentTerm(pay_term="180"),
    ])


def create_extra_pay_methods():
    """Create additional payment methods for testing."""
    PaymentMethod.objects.bulk_create([
        PaymentMethod(pay_method="Debit Card"),
        PaymentMethod(pay_method="Check"),
    ])

"""Back end custom functinos"""
def get_file(file_path):
    """
    Open a file for testing.
    Parameteres:
    - file_path: location of the file.
    """
    file_path = Path.cwd()/file_path
    
    # Check extension to assing correct content_type
    extension = file_path.suffix
    if extension == ".csv":
        content_type = "text/csv"
    elif extension == ".xls":
        content_type = "application/vnd.ms-excel"
    elif extension == ".xlsx":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif extension == ".pdf":
        content_type = "application/pdf"
    else: 
        raise ValueError("Wrong file extension.")
    
    # Open file and post
    with open(file_path, "rb") as file:
        uploaded_file = SimpleUploadedFile(file.name, file.read(),
            content_type=content_type)
    
    return uploaded_file


"""Selenium custom functions"""
# General actions
def go_to_section(driver, module, section_index):
    """
    Go to a section of the navbar.
    Parameters: 
    - driver: web driver, 
    - module: client/supplier, etc, 
    - section_index: Index of module's section: overview, new, edit, etc.
    """
    driver.find_element(By.ID, f"{module}-menu-link").click()
    path = driver.find_element(By.ID, f"{module}-menu")
    path.find_elements(By.CLASS_NAME, "dropdown-item")[section_index].click()

def go_to_link(driver, selector, parent_selector_name, url, link_index=0):
    """
    Simplify the necessary code to click a link and wait till the page change.
    Parameters:
    - driver: WebDriver.
    - selector: WebDrvier's selector. IE: By.TAG_NAME, By.CLASS_NAME, etc.
    - parent_selector_name: Selector's name of parent element.
    - url: Url that should change after clicking.
    - link_index: Index of link element. Default: 0.

    """
    path = driver.find_element(selector, parent_selector_name)
    path.find_elements(By.TAG_NAME, "a")[link_index].click()
    WebDriverWait(driver, 10).until(EC.url_changes(url))

def click_and_wait(driver, element_id, waiting_time=0.5):
    """
    Click an element and wait a certain time.
    Parameters:
    - driver: WebDriver
    - element_id: id of the element I want to click.
    - waiting_time: Time to wait after clicking. Default 2.
    """
    driver.find_element(By.ID, element_id).click()
    time.sleep(waiting_time)

def click_and_redirect(driver, selector, selector_name, current_url, 
        parent_element=None):
    """
    Do a click on an element and wait until current url changes.
    Paramenters:
    - driver: WebDriver.
    - selector: Selector name for finding the target element.
    - selector_name: Selector's name of the element, necessary for searching it.
    - current_url: Current url before clicking.
    - parent_element: Parent element of the target one. Default: None.
    """
    root = parent_element or driver
    root.find_element(selector, selector_name).click()
    WebDriverWait(driver, 10).until(EC.url_changes(current_url))

def click_button_and_show(driver, parent_selector, parent_name, show_selector, 
    show_name, index=0):
    """
    Click a button and wait unti an element is showed.
    Parameters:
    - driver: WebDriver.
    - parent_selector: Selector of the buttons's parent element.
    - parent_name: Name of button's parent element searched by the selector.
    - show_selector: Selector of the new element that will be showed.
    - show_name: Element's name searched by the selector.
    - index: If there are multiple buttons, index number. Default: 0. 
    """
    path = driver.find_element(parent_selector, parent_name)
    path.find_elements(By.TAG_NAME, "button")[index].click()
    webDriverWait_visible_element(driver, show_selector, show_name)





def fill_field(driver, path, field, value):
    """
    Pick, clean and fill a field. It waits until the value is loaded on page.
    Parameters: 
    - driver: WebDriver
    - path: parent element of field.
    - field: tax_number, etc.
    - value: value of the field to submit.  
    """
    # Clear and add value in input
    selected_field = path.find_element(By.NAME, field)
    selected_field.clear()
    selected_field.send_keys(value)
    
    # Wait until input was added
    selected_field = path.find_element(By.NAME, field)
    input_value = selected_field.get_attribute("value")

    WebDriverWait(driver, 10).until(
        lambda driver: input_value == value
    )

def element_has_selected_option(locator, option_text):
    """
    Returns True if selected option has an especific text.
    Paramenters: 
    - locator: location of the element; 
    - option_text: text I want to compare.
    """
    def _predicate(driver):
        # Search and add class to select element
        select_element = Select(driver.find_element(*locator))
        # Pick selected option
        selected_option = select_element.first_selected_option
        # Return True if text is in selected option
        return selected_option.text == option_text
        # Return function to be used by webdriver
    return _predicate

def pick_option_by_index(driver, element_id, index, expected_value):
    """
    Get an element with options and select index
    Parameters: 
    - driver: WebDriver. 
    - element_id: id of element that has the options.
    - index: Number of option I want to pick
    - expected_value: value that selected option should have.
    """
    Select(driver.find_element(By.ID, element_id)).select_by_index(index)
    WebDriverWait(driver, 10).until(
        element_has_selected_option((By.ID, element_id), expected_value)
    )
    

def get_columns_data(row, start=0, end=-1):
    """
    Return all the data from columns.
    Parameters: 
    - row: row element container of each cell.
    - start: Starting column.
    - end: ending column.
    """
    row_data = row.find_elements(By.TAG_NAME, "td")
    for i in range(start, end):
        yield row_data[i]

def webDriverWait_visible_element(driver, selector, element_name): 
    """
    Clearer line of WebDriveWait visibility of element located. Wait 10 secs.
    Parameters:
    - driver: WebDriver.
    - selector: Element selector. By.CLASS_NAME, By.TAG_NAME, etc.
    - selector_name: Name of the element that the selector will search.
    """
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((selector, element_name))
    )

def click_button_and_answer_alert(driver, parent_selector, parent_name, 
    alert_answer, index=0):
    """
    Click on a button and then answer an alert
    Parameters:
    - driver: WebDriver.
    - parent_selector: Selector of the buttons's parent element.
    - parent_name: Name of button's parent element searched by the selector.
    - alert_answer: Accept/Cancel the alert.
    - index: If there are multiple buttons, index number. Default: 0. 
    """
    path = driver.find_element(parent_selector, parent_name)
    path.find_elements(By.TAG_NAME, "button")[index].click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    if alert_answer == "accept":
        driver.switch_to.alert.accept()
    elif alert_answer == "dismiss":
        driver.switch_to.alert.dismiss()


# By section functions

def delete_person_click_on_delete(driver): # TODO
    """In delete client/supplier section, click on delete button"""
    path = driver.find_element(By.ID, "person-details")
    path.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())

def pay_conditions_click_default(driver, condition_index):  # TODO
    """
    In payment conditions sections, cLick on default button.
    Paramenters: 
    - driver: WebDriver.
    - conditions_index: 0 is term, 1 is method.
    """
    path = driver.find_elements(By.CLASS_NAME, "default-button")
    path[condition_index].click()
    
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

def pay_conditions_delete_confirm_button(driver, path):
    """
    In payment conditions section, click on delete and confirm.
    Paramenters: 
    - driver: web driver; 
    - path: location of delete button.
    """
    delete_button = path.find_elements(By.CLASS_NAME, "delete-item")[1]
    delete_button.click()  
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "view-list"),
            "Confirm"
        )
    )
    # Click in confirm
    delete_button.click()
    WebDriverWait(driver, 10).until(EC.staleness_of(delete_button))

def search_fill_field(driver, element_id, value):
    """
    While searching, fill the field to search.
    Parameters:  
    - driver: Webdriver; 
    - element_id: id of field I want to fill;
    - value: Value to insert in field;
    """
    field = driver.find_element(By.ID, element_id)
    # I use action chains as sometimes there's conflict with regular click and
    # key sending."
    ActionChains(driver).move_to_element(field).click(field).perform()
    for char in value:
        ActionChains(driver).send_keys(char).perform()
        time.sleep(0.05)

def search_clear_field(driver, element_id, first_element_list=None):
    """
    Clear the searched field using ActionChains and explicit backspace.
    Parameters: 
    - driver: Webdriver.
    - element_id: id of field I want to clear.
    - first_element_list: First element of the list that should be cleared at
    the end. Optional (if there are multiple fields completed, WebDriverWait 
    won't work).
    """
    field = driver.find_element(By.ID, element_id)
    action = ActionChains(driver).move_to_element(field).click(field)
    for char in field.get_attribute("value"):
        action.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.05)
    if first_element_list:
        WebDriverWait(driver, 10).until(EC.staleness_of(first_element_list))

def search_first_input(driver, path, id_element, input, count):
    """
    As it's the first input, sometimes selenium doesn't load the script properly,
    so that, it refreshes the input up to 3 times.
    Note: Wait for script to be ready, time.sleeps and looping explicit waits 
    were attemped before and they didn't work or they're time consuming.
    Parameters:
    - driver: WebDriver;
    - path: Parent of the list to check count; 
    - id_element: element to write imput and clean;
    - input: data to write on the element;
    - count: expected number of list's instances.
    """
    for i in range(3):
        try:
            return web_driver_wait_count(driver, path, count)
        except ValueError:
            search_clear_field(driver, id_element)
            search_fill_field(driver, id_element, input)
    return web_driver_wait_count(driver, path, count)

# WebDriver functions
def web_driver_wait_count(driver, path, count, list_tag="li"):
    """
    Custom webdriverwait that compares the number of elements in a list with the
    expected count. It returns the updated list or it raises a ValueError. 
    Parameters: 
    - driver: WebDriver;
    - path: Parent of the list to check count; 
    - count: Expected count.
    - list_tag: tag_name of the list. Default: "li".
    Returns:
    - Updated version of doc_list
    - Value error: When couldn't find the match.
    """
    # Update list before waiting
    doc_list = path.find_elements(By.TAG_NAME, list_tag)
    
    try: 
        WebDriverWait(driver, 1).until(lambda d: len(doc_list) == count)
        return doc_list
    except TimeoutException:
        raise ValueError(
            f"web_driver_wait_count failed. Expected list len: {count}, "
            f"list_len output: {len(doc_list)}."
        )