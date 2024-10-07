""" Custom functions for testing files"""
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from ..models import Payment_term, Payment_method

"""DB custom functions"""
def create_extra_pay_terms():
    """Create additional payment terms for testing."""
    Payment_term.objects.bulk_create([
        Payment_term(pay_term="90"),
        Payment_term(pay_term="180"),
        Payment_term(pay_term="360"),
    ])

def create_extra_pay_methods():
    """Create additional payment methods for testing."""
    Payment_method.objects.bulk_create([
        Payment_method(pay_method="Transfer"),
        Payment_method(pay_method="Check"),
    ])


"""Selenium custom functions"""
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

def edit_person_click_on_person(driver, person_index):
    """
    Click on client/supplier in edit section
    Parameters:
    - driver: WebDriver.
    - person_number: Index of the client/supplier I want to click.
    """
    path = driver.find_elements(By.CLASS_NAME, "specific-person")
    path[person_index].click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "person-details"))
    )

def edit_person_click_on_edit(driver):
    """Click in edit button after clicking a client/supplier in edit section"""
    path = driver.find_element(By.ID, "person-details")
    path.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "person-edit-form"))
    )

def fill_field(path, field, value):
    """
    While editing a client/supplier, fill a field.
    Parameters: 
    - path: parent element of field; 
    - field: tax_number, etc.;
    - value: value of the field to submit.  
    """
    selected_field = path.find_element(By.NAME, field)
    selected_field.clear()
    selected_field.send_keys(value)
    path.find_element(By.TAG_NAME, "button").click()

def delete_person_click_on_delete(driver):
    """In delete client/supplier section, click on delete button"""
    path = driver.find_element(By.ID, "person-details")
    path.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())

def pay_conditions_click_default(driver, condition_index):  
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

def search_fill_field(driver, element_id, value):
    """
    While searching, fill the field to search.
    Parameters:  
    - driver: Webdriver; 
    - element_id: id of field I want to fill;
    - value: Value to insert in field;
    """
    field = driver.find_element(By.ID, element_id)
    ActionChains(driver).move_to_element(field).click(field).perform()
    for char in value:
        ActionChains(driver).send_keys(char).perform()
        time.sleep(0.1)

def search_clear_field(driver, element_id):
    """
    While searching, clear the searched field.
    Parameters: 
    - driver: Webdriver; 
    - element_id: id of field I want to clear;
    """
    field = driver.find_element(By.ID, element_id)
    action = ActionChains(driver).move_to_element(field).click(field)
    for i in range(len(field.get_attribute("value"))):
        action.send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.1)

def get_columns_data(row, start=0, end=-1):
    """
    Return all the data from columns in one go.
    Parameters: 
    - row: row element container of each cell.
    - start: Starting column.
    - end: ending column.
    """
    row_data = row.find_elements(By.TAG_NAME, "td")
    for i in range(start, end):
        yield row_data[i]

def manual_explicit_wait(path, doc_list, condition, time_limit=2):
    """
    Manual explicit wait for tests when ExplicitWait doesn't work properly. It
    check the codition every 0.2 secs.
    Parameters: 
    - path: parent element of doc_list; 
    - doc_list: 
    - list to check condition; 
    - condition: condition that keeps true the loop.
    - time_limit: In secs, indicates the time limit of tries. Default: 2
    Returns:
    - Updated version of doc_list
    """
    current_time = 0
    while len(doc_list) != condition and current_time < time_limit:
        time.sleep(0.2)
        doc_list = path.find_elements(By.TAG_NAME, "li")
        current_time += 0.2
    
    if current_time > time_limit:
        raise ValueError(
            f"manual_explicit_waiting used and time limit ({time_limit}) exceeded."
            f"Expected list len: {condition}, list_len output: {len(doc_list)}."
        )

    return doc_list

def click_and_wait(driver, element_id, waiting_time=1.5):
    """
    Click an element and wait a certain time.
    Parameters:
    - driver: WebDriver
    - element_id: id of the element I want to click.
    - waiting_time: Time to wait after clicking. Default 2.
    """
    driver.find_element(By.ID, element_id).click()
    time.sleep(waiting_time)