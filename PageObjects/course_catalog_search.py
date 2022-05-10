import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import sql_scripts

term_to_premadb_convert = {
    "2": 1,  # Fall
    "3": 2,  # Spring
    "1": 3,  # First Summer
    "5": 5,  # Six Week Summer
    "4": 4  # Second Summer
}
# Give me a Rumad day and I'll give you a premaDB d_id
rumad_day_to_prema_day_convert = {
    "L": 1,
    "M": 2,
    "W": 3,
    "J": 4,
    "V": 5,
    "S": 6
}


def get_active_semesters_and_parse(driver: WebDriver):
    active_semesters = driver.find_elements(By.XPATH, '//*[@id="ui_menu_area"]/form/div[1]/select//*')
    active_semester_dicts = []
    for element in active_semesters:
        term, year = element.get_attribute("value").split("|")
        semester = {"term": term_to_premadb_convert[term], 'value': element.get_attribute("value"), "year": int(year)}
        active_semester_dicts.append(semester)
    return active_semester_dicts[::-1]


def get_or_create_semester_return_id(semester):
    return sql_scripts.get_or_create_semester_return_id(semester)


def build_search_course_url(semester, course):
    four_letter_code = course[0][:4]
    four_number_code = course[0][4:]
    return f"https://home.uprm.edu/horario.php?action=show&fseries={four_letter_code}&fnum={four_number_code}&fsem={semester['value']} "


# semesterOffers = [(section, capacity, start_time, end_time, classroom, professor, days_id_list), (...)]
def get_all_semester_offers_from_page(driver, semester, course):
    semester_offers = []
    try:
        elements = driver.find_element(By.XPATH, "//*[@id=\"ui_body_area\"]/form/table/tbody")
    except:
        return []
    count = 0
    for table_row in elements.find_elements(By.XPATH, value=".//tr"):
        if count == 0:
            count += 1
            continue
        table_data = table_row.find_elements(By.XPATH, value=".//td")
        semester_offers.append(extract_semester_offer_from_table_helper(table_data, semester, course))
    return semester_offers


# Some string manipulation
def extract_semester_offer_from_table_helper(table_data, semester, course):
    section = table_data[0].accessible_name[9:]
    capacity = int(table_data[1].accessible_name)
    professor = table_data[5].accessible_name
    string_pieces = table_data[4].accessible_name.split(' ')
    if section[-1] != 'D':
        try:
            start_time = string_pieces[0] + string_pieces[1]
            end_time = string_pieces[3] + string_pieces[4]
            classroom = string_pieces[-2].strip() + string_pieces[-1]
            days = string_pieces[5].strip()
            days_id_list = []
            for day in days:
                days_id_list.append(rumad_day_to_prema_day_convert[day])
            semester_offer_has_reunion = True
        except:
            start_time, end_time, classroom, days_id_list = None
            print('Error with the following data: ' + str(table_data[4].accessible_name))
            print('The following Course: ' + str(course) + 'does not have a physcial reunions. It is probably using '
                                                           'distance modality.')

    return section, capacity, start_time, end_time, classroom, professor, days_id_list


def semester_offer_data_exists_in_prod(semester_offer_data, semester_id, course_id):
    return sql_scripts.semester_offer_data_exists_in_prod(semester_offer_data, semester_id, course_id)


def remove_and_create_timelots(semester_offer_data):
    pass


def create_semesterOffer_with_timeslots(semester_offer_data, semester_id, course_id):
    semester_offer_id = sql_scripts.create_semester_offer(semester_offer_data, semester_id, course_id)
    sql_scripts.create_semester_offer_timeslots(semester_offer_data, semester_offer_id)


def handle_semester_offer_without_reunions(semester_offer_data):
    pass


def course_catalog_search(driver: WebDriver):
    driver.get("https://home.uprm.edu/students/index.php")
    course_catalog_btn = driver.find_element(By.XPATH, '//*[@id="ui_body_area"]/div[1]/div[21]/a')
    course_catalog_btn.click()
    semesters = get_active_semesters_and_parse(driver)
    course_list = sql_scripts.get_course_list()

    # TODO REMEMBER TO HANDLE PROFESSOR TEACHES RELATION -> (SO_ID, P_ID),
    #  I HAVE TO ADD THIS WHEN I CREATE A SEMESTER OFFER,
    #  WHILE AT IT MAYBE CREATE A LIST OF PROFESSORS NOT FOUND IN PREMADB TO INNVESTIGATE LATER..

    for semester in semesters:
        semester_id = get_or_create_semester_return_id(semester)
        for course in course_list:
            time.sleep(2)
            url = build_search_course_url(semester, course)
            driver.get(url)
            semester_offer_data_list = get_all_semester_offers_from_page(driver, semester, course)

            if len(semester_offer_data_list) == 0:
                continue

            for semester_offer_data in semester_offer_data_list:
                # TODO handle different cases of semester Offers, some might not have times,
                #  others might have times but no classrooms, etc... Special cases
                #  this cases will mainly be addressed inside extract_semester_offer_from_table_helper
                if semester_offer_data[2] is None:
                    handle_semester_offer_without_reunions(semester_offer_data)
                    continue
                so_id = semester_offer_data_exists_in_prod(semester_offer_data, semester_id, course[1])
                if so_id > -1:
                    remove_and_create_timelots(semester_offer_data, so_id)
                    continue
                create_semesterOffer_with_timeslots(semester_offer_data, semester_id, course[1])
