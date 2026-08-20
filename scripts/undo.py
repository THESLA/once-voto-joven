import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from crear_formulario_egresados import CHROMEDRIVER, log

EDITOR_URL = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR_URL)
    time.sleep(4)

    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL, "z")
    time.sleep(3)
    tb = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
    log(f"preguntas tras undo: {len(tb)}")
    driver.quit()


if __name__ == "__main__":
    main()
