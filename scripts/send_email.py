import sys, time
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from crear_formulario_egresados import CHROMEDRIVER, log, wait_for, js_click

def to_input(driver):
    return next(iter(driver.find_elements(By.XPATH, "//input[@aria-label[contains(.,'Destinatarios en Para')]]")), None)

def subjectbox(driver):
    return next(iter(driver.find_elements(By.CSS_SELECTOR, "input[name='subjectbox']")), None)

def body_area(driver):
    return (next(iter(driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")), None)
            or next(iter(driver.find_elements(By.XPATH, "//textarea[@aria-label='Cuerpo del mensaje']")), None))

def send_btn(driver):
    return next(iter(driver.find_elements(By.XPATH,
        "//input[@type='submit' and (@value='Enviar' or @alt='Enviar')]"
        "| //input[@type='image' and (@value='Enviar' or @alt='Enviar')]"
        "| //div[@role='button' and (contains(@data-tooltip,'Enviar') or contains(@data-tooltip,'Send'))]")), None)

GMAIL = "https://mail.google.com/"
TO = "sanluistrabajosestudiantes@gmail.com"
SUBJECT = "Actividad: Encuesta de estudiantes de grado once - Colegio San Luis"
LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdBOk474lR5TCeZMHmrYXwb8HohcV9YmvoASa_2Bi6MUSpVAw/viewform"
BODY = ("Cordial saludo,\n\n"
        "Este es el enlace a la encuesta de los estudiantes de grado once del Colegio San Luis. "
        "Es una actividad que deben completar: por favor respondan la encuesta.\n\n"
        + LINK + "\n\n"
        "Gracias.\nColegio San Luis")

def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    # Pestaña nueva limpia y controlada (evita colisiones con pestañas abiertas)
    driver.switch_to.new_window('tab')
    time.sleep(1)

    # Redacción directa (formulario legado pre-rellenado)
    url = ("https://mail.google.com/mail/u/0/?view=cm&fs=1&tf=1"
           f"&to={quote(TO)}&su={quote(SUBJECT)}&body={quote(BODY)}")
    driver.get(url)
    time.sleep(6)

    # Destinatario
    ti = wait_for(to_input, "campo Destinatario", 30)
    if not (ti.get_attribute('value') or ""):
        ti.click()
        ti.send_keys(TO)
        time.sleep(1)
        ti.send_keys(Keys.ENTER)
        time.sleep(1)

    # Asunto
    sb = wait_for(subjectbox, "campo Asunto", 15)
    cur = sb.get_attribute('value') or ""
    if not cur:
        sb.click(); sb.send_keys(SUBJECT)
        time.sleep(0.5)

    # Cuerpo
    ba = wait_for(body_area, "cuerpo", 10)
    if not (ba.text or ba.get_attribute('value') or "").strip():
        ba.click(); ba.send_keys(BODY)
        time.sleep(1)

    log(f"Para: {(ti.get_attribute('value') or '')}")
    log(f"Asunto: {(sb.get_attribute('value') or '')}")
    log(f"Cuerpo palabras: {len((ba.text or '').split())}")

    send = wait_for(send_btn, "botón Enviar", 15)
    js_click(driver, send)
    time.sleep(4)
    log("✅ EMAIL ENVIADO")
    driver.quit()


if __name__ == "__main__":
    main()
