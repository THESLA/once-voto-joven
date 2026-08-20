import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"
TARGET = "Registro de Estudiantes – Colegio San Luis"


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(14)

    for attempt in range(8):
        el = next(iter(driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Form title']")), None)
        if el is None:
            log(f"  intento {attempt+1}: no encontré el título")
            time.sleep(2)
            continue
        try:
            ActionChains(driver).move_to_element(el).click().perform()
        except Exception:
            driver.execute_script("arguments[0].focus()", el)
        time.sleep(0.4)
        el = next(iter(driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Form title']")), None)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(TARGET)
        time.sleep(1.0)
        cur = (next(iter(driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Form title']")), None).text or "").strip()
        log(f"  intento {attempt+1}: título → {cur!r}")
        if cur == TARGET:
            break
        time.sleep(1.0)

    driver.quit()


if __name__ == "__main__":
    main()
