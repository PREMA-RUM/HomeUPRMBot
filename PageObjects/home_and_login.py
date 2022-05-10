from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from config import config


def home_and_login(driver: WebDriver):
    driver.get("https://home.uprm.edu")

    email_input = driver.find_element(By.XPATH, "/html/body/div/div[2]/table/tbody/tr/td[2]/form/table/tbody/tr[1]/td[1]/input")
    password_input = driver.find_element(By.XPATH, "/html/body/div/div[2]/table/tbody/tr/td[2]/form/table/tbody/tr[2]/td/input")
    submit_btn = driver.find_element(By.XPATH, "/html/body/div/div[2]/table/tbody/tr/td[2]/form/table/tbody/tr[1]/td[2]/input[2]")

    email_input.send_keys(config.uprm_email)
    password_input.send_keys(config.uprm_password)
    submit_btn.click()
