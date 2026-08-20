import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log, question_card

import sys

EDITOR_URL = sys.argv[1] if len(sys.argv) > 1 else "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR_URL)
    time.sleep(4)

    tbs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
    log(f"TOTAL PREGUNTAS: {len(tbs)}")
    for i in range(len(tbs)):
        card = question_card(driver, i)
        title_el = card.find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
        title = (title_el.text or "")[:70]
        tipo_el = card.find_element(By.XPATH, ".//*[@role='listbox' and @aria-label='Question types']")
        tipo = (tipo_el.get_attribute("value") or tipo_el.text or "")[:30]
        list_el = card.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
        opts = []
        if list_el:
            vals = list_el[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")
            opts = [(v.get_attribute("value") or "")[:22] for v in vals]
        req = card.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")
        req_state = req[0].get_attribute("aria-checked") if req else "?"
        log(f"P#{i+1} [{tipo}] req={req_state} :: {title} :: {opts}")
    driver.quit()


if __name__ == "__main__":
    main()
