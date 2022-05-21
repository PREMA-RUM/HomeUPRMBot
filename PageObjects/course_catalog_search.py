import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import sql_scripts
from Models.Semesteroffer import SemesterOfferTableData, TimeSlotTableData

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


def extract_timeslots_from_reuniones(reunion_data):
    timeslot_list = []
    classroom = ''
    for reunion in reunion_data:
        if len(reunion) == 0:
            continue
        reunion_pieces = reunion.split(' ')
        reunion_pieces = list(filter(lambda a: a != '', reunion_pieces))
        try:
            classroom = reunion_pieces[6] + reunion_pieces[7]
        except:
            classroom = ''

        for day in reunion_pieces[5]:
            timeslot_list.append(TimeSlotTableData(start_time=reunion_pieces[0] + reunion_pieces[1],
                                                   end_time=reunion_pieces[3] + reunion_pieces[4],
                                                   day_id=rumad_day_to_prema_day_convert[day]))
    return timeslot_list, classroom


def extract_semester_offer_from_table_helper(table_data, semester, course):
    section = table_data[0].accessible_name[9:]
    capacity = int(table_data[1].accessible_name)
    professor_list = table_data[5].text.split('\n') if table_data[5].text != '' else []
    for i, professor in enumerate(professor_list):
        if "'" in professor:
            print(professor)
            professor_list[i] = professor.replace("'", "`")
    time_slot_list, classroom = extract_timeslots_from_reuniones(table_data[4].text.split('\n'))

    return SemesterOfferTableData(section=section, capacity=capacity, professor=professor_list, classroom=classroom,
                                  slots=time_slot_list)


def semester_offer_data_exists_in_prod(semester_offer, semester_id, course_id):
    return sql_scripts.semester_offer_data_exists_in_prod(semester_offer, semester_id, course_id)


def update_semester_offer(semester_offer, so_id, semester_id):
    sql_scripts.update_semester_offer(semester_offer, so_id, semester_id)
    create_professors_and_professor_teaches(semester_offer, so_id)


def remove_and_create_timelots(semester_offer, so_id):
    sql_scripts.remove_timeslots(so_id)
    if semester_offer.slots is not None and len(semester_offer.slots) > 0:
        sql_scripts.create_semester_offer_timeslots(semester_offer, so_id)


def create_semesterOffer_with_timeslots(semester_offer, semester_id, course_id):
    semester_offer_id = sql_scripts.create_semester_offer(semester_offer, semester_id, course_id)

    create_professors_and_professor_teaches(semester_offer, semester_offer_id)

    if semester_offer.slots is not None and len(semester_offer.slots) > 0:
        sql_scripts.create_semester_offer_timeslots(semester_offer, semester_offer_id)


def create_professors_and_professor_teaches(semester_offer, semester_offer_id):
    if len(semester_offer.professor) > 0:
        sql_scripts.remove_professor_teaches(semester_offer_id)
        professor_ids, missing_professors = sql_scripts.get_professor_id(semester_offer)
        if len(missing_professors) > 0:
            professor_ids += sql_scripts.create_professor(missing_professors)
        sql_scripts.add_professor_teaches(semester_offer_id, professor_ids)


def course_catalog_search(driver: WebDriver):
    driver.get("https://home.uprm.edu/students/index.php")
    course_catalog_btn = driver.find_element(By.XPATH, '//*[@id="ui_body_area"]/div[1]/div[21]/a')
    course_catalog_btn.click()
    semesters = get_active_semesters_and_parse(driver)
    course_list = sql_scripts.get_course_list()

    for semester in semesters:
        print(semester)
        semester_id = get_or_create_semester_return_id(semester)
        course_count = 0
        for course in course_list:
            course_count += 1
            url = build_search_course_url(semester, course)
            print('Fetching: ', url, 'Course:', course_count, ' of ', len(course_list))
            driver.get(url)
            semester_offer_list = get_all_semester_offers_from_page(driver, semester, course)

            if len(semester_offer_list) == 0:
                continue

            for semester_offer in semester_offer_list:
                so_id = semester_offer_data_exists_in_prod(semester_offer, semester_id, course[1])
                if so_id > -1:
                    update_semester_offer(semester_offer, so_id, semester_id)
                    remove_and_create_timelots(semester_offer, so_id)
                    continue
                create_semesterOffer_with_timeslots(semester_offer, semester_id, course[1])
        sql_scripts.connection.commit()
