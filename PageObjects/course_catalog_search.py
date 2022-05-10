from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

import sql_scripts

term_to_premadb_convert = {
    "2": "Fall",
    "3": "Spring",
    "1": "First Summer",
    "5": "Six Week Summer",
    "4": "Second Summer"
}

to_dec_year = ["First Summer", "Second Summer", "Six Week Summer"]

def get_active_semesters_and_parse(driver: WebDriver):
    active_semesters = driver.find_elements(By.XPATH, '//*[@id="ui_menu_area"]/form/div[1]/select//*')
    active_semester_dicts = []
    for element in active_semesters:
        term, year = element.get_attribute("value").split("|")
        semester = {"term": term_to_premadb_convert[term], 'value': element.get_attribute("value")}
        if term_to_premadb_convert[term] in to_dec_year:
            semester["year"] = int(year) - 1
        else:
            semester["year"] = int(year)
        active_semester_dicts.append(semester)
    return active_semester_dicts[::-1]

def course_catalog_search(driver: WebDriver):
    driver.get("https://home.uprm.edu/students/index.php")

    course_catalog_btn = driver.find_element(By.XPATH, '//*[@id="ui_body_area"]/div[1]/div[21]/a')
    course_catalog_btn.click()
    # https://home.uprm.edu/horario.php?r=1&fsem=5|2022
    # https://home.uprm.edu/horario.php?action=show&fseries=CIIC&fnum=3075&fsem=5|2022
    semesters = get_active_semesters_and_parse(driver)
    course_list = sql_scripts.get_course_list()







