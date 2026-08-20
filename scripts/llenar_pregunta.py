import sys
import time

sys.path.insert(0, r"C:\Users\RoSH\Documents\Once\scripts")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log

DRAFT = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"


def type_editable(driver, el, text):
    try:
        ActionChains(driver).move_to_element(el).click().perform()
    except Exception:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
    time.sleep(0.3)
    el.send_keys(Keys.CONTROL, "a")
    el.send_keys(text)
    time.sleep(0.6)
    return (el.text or "").strip()


def main():
    qidx = int(sys.argv[1]) - 1
    text = sys.argv[2]

    opts = Options()
    opts.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    try:
        driver.execute_script("window.open('about:blank');")
        time.sleep(1)
        for h in driver.window_handles:
            driver.switch_to.window(h)
            if driver.current_url.startswith("about:blank"):
                break
        driver.get(DRAFT)
        time.sleep(7)

        filled = ""
        for attempt in range(3):
            qs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
            if qidx >= len(qs):
                log(f"⛔ Solo hay {len(qs)} preguntas; índice {qidx+1} no existe")
                sys.exit(1)
            tb = qs[qidx]
            filled = type_editable(driver, tb, text)
            if filled == text:
                break
            log(f"  intento {attempt+1}: quedó {filled[:40]!r}")
        if filled == text:
            log(f"✅ P#{qidx+1} título OK: {text}")
        else:
            log(f"⚠ P#{qidx+1} NO guardó: {filled[:40]!r}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
