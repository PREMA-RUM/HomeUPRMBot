import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import sql_scripts

'''
INSERT INTO 
                Users (user_name, user_password, user_email, user_balance, role_id) VALUES
                (%s, %s, %s, 0.00, (SELECT role_id FROM Roles WHERE role_name='User' LIMIT 1))
                RETURNING user_id, user_name, user_email, user_password, user_balance, role_id;

'''

term_to_premadb_convert = {
    "2": 1,  # Fall
    "3": 2,  # Spring
    "1": 3,  # First Summer
    "5": 5,  # Six Week Summer
    "4": 4  # Second Summer
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
    return f"https://home.uprm.edu/horario.php?action=show&fseries={four_letter_code}&fnum={four_number_code}&fsem={semester['value']}"


def get_all_semester_offers_from_page(driver):
    try:
        elements = driver.find_element(By.XPATH, "//*[@id=\"ui_body_area\"]/form/table/tbody")
    except:
        return []
    print(elements)
    count = 0
    for table_row in elements.find_elements(By.XPATH, value=".//tr"):
        if count == 0:
            count += 1
            continue
        table_data = table_row.find_elements(By.XPATH, value=".//td")
        section = table_data[0].accessible_name[9:]
        capacity = int(table_data[1].accessible_name)
        time_and_classroom = table_data[4].accessible_name
        professor = table_data[5].accessible_name


    return []



def semester_offer_data_exists_in_prod(semester_offer_data, semester_id, param):
    pass


def remove_and_create_timelots(semester_offer_data):
    pass


def create_semesterOffer(semester_offer_data, semester_id, param):
    pass


def course_catalog_search(driver: WebDriver):
    driver.get("https://home.uprm.edu/students/index.php")

    course_catalog_btn = driver.find_element(By.XPATH, '//*[@id="ui_body_area"]/div[1]/div[21]/a')
    course_catalog_btn.click()
    # https://home.uprm.edu/horario.php?r=1&fsem=5|2022
    semesters = get_active_semesters_and_parse(driver)
    course_list = sql_scripts.get_course_list()
    print(course_list)



# TODO REMEMBER TO HANDLE PROFESSOR TEACHES RELATION OF (SO_ID, P_ID)

    for semester in semesters:
        semester_id = get_or_create_semester_return_id(semester)
        for course in course_list:
            time.sleep(2)
            url = build_search_course_url(semester, course)
            driver.get(url)
            semester_offer_data_list = get_all_semester_offers_from_page(driver)

            if len(semester_offer_data_list) == 0:
                continue

            for semester_offer_data in semester_offer_data_list:
                if semester_offer_data_exists_in_prod(semester_offer_data, semester_id, course[1]):
                    remove_and_create_timelots(semester_offer_data, )
                    continue

                create_semesterOffer(semester_offer_data, semester_id, course[1])

# iterar por cada semestre
# Si no existe el semestre, crearlo en prod. Guardar el Id del semestre en una variable para fuitura referencia.
# por cada curso,
# buscarlo en el semestre usando el url
# Si existe un semester offer en rumad
# verifico si existe en prod usando (c_id, s_id, section)
# si existe en prod
# borrar timeslots de los semesterOffers en prod
# 'scrapeo' nuevos timeslots de rumad
# anado timeslots a prod
# else
#  crear semesterOffer con info de rumad
# anado relacion de timeslot a semesterOffer creado
# si no existe en rumad
# continue
