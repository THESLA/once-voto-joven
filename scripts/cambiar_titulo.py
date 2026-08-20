import sys, time
sys.path.insert(0, r"C:\Users\RoSH\Documents\Once\scripts")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from crear_formulario_egresados import CHROMEDRIVER, log, last_textbox

DRAFT = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"
NEW = "Registro de Estudiantes – Colegio San Luis"

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
    for attempt in range(4):
        tb = last_textbox(driver, "Form title")
        filled = type_editable(driver, tb, NEW)
        log(f"intento {attempt+1}: {filled[:45]!r}")
        if filled == NEW:
            break
    log("✅ TÍTULO: " + (filled if filled == NEW else "⚠ FALLÓ — " + filled))
finally:
    driver.quit()
