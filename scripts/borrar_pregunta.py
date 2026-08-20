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
    n = int(sys.argv[1])  # 1-based número de pregunta
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR_URL)
    time.sleep(4)

    before = len(titles(driver))
    card = question_card(driver, n - 1)
    texto = (card.find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']").text or "")[:50]
    delete_btn = card.find_element(By.XPATH, ".//*[@aria-label='Delete question']")
    robust_click(driver, delete_btn)
    time.sleep(3)
    after = len(titles(driver))
    log(f"BORRAR P#{n} ('{texto}') antes={before} despues={after}")
    for i in range(min(5, after)):
        log(f"  queda P#{i+1}: {(titles(driver)[i].text or '')[:45]}")
    driver.quit()


if __name__ == "__main__":
    main()
