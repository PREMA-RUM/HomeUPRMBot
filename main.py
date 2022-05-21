import time

from selenium import webdriver

from PageObjects.course_catalog_search import course_catalog_search
from PageObjects.home_and_login import home_and_login
import sql_scripts

from config import config


def main():
    try:
        chromedriver = config.web_driver
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(chromedriver, options=options)
        home_and_login(driver)
        course_catalog_search(driver)
        driver.close()
    except BaseException as e:
        print("Something failed", str(e))
    finally:
        sql_scripts.connection.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
