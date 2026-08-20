import sys, time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log, question_card, robust_click

EDITOR_URL = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"


def titles(driver):
    return driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR_URL)
    time.sleep(4)

    log(f"preguntas antes: {len(titles(driver))}")
    card = question_card(driver, 4)
    delete_btn = card.find_element(By.XPATH, ".//*[@aria-label='Delete question']")
    robust_click(driver, delete_btn)
    time.sleep(3)

    tb = titles(driver)
    log(f"preguntas después: {len(tb)}")
    for i in range(min(4, len(tb))):
        log(f"P#{i+1}: {tb[i].get_attribute('value')}")
    driver.quit()


if __name__ == "__main__":
    main()
