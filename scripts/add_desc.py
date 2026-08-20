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
TITULO = "Registro de Estudiantes – Colegio San Luis"
DESC = ("Esta encuesta recopila la información de los estudiantes del grado once para crear una base de datos del Colegio San Luis. "
        "Estos datos nos permitirán mantener el contacto con ustedes en el futuro, convocarlos a reuniones y actividades de la promoción, "
        "y conservar el tejido social que se construye en el colegio. La información quedará guardada de forma segura y solo se usará con estos fines.")


def campo_desc():
    for sel in ["[aria-label='Form description']", "[aria-label='Description']"]:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            return els[0]
    return None


def set_field(el_xpath, text, label):
    for a in range(8):
        el = next(iter(driver.find_elements(By.XPATH, el_xpath)), None)
        if el is None:
            log(f"  {label}: no encontrado")
            time.sleep(2)
            continue
        try:
            ActionChains(driver).move_to_element(el).click().perform()
        except Exception:
            driver.execute_script("arguments[0].focus()", el)
        time.sleep(0.4)
        el = next(iter(driver.find_elements(By.XPATH, el_xpath)), None)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(text)
        time.sleep(1.0)
        cur = (next(iter(driver.find_elements(By.XPATH, el_xpath)), None).text or "").strip()
        log(f"  {label} intento {a+1}: {cur[:45]!r}")
        if cur == text:
            return True
        time.sleep(1.0)
    return False


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    global driver
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(14)

    log("== Título ==")
    set_field("//*[@role='textbox' and @aria-label='Form title']", TITULO, "título")

    # descripción: probar por atributos; si no, dump cerca del título
    el = campo_desc()
    if el is None:
        log("descripción: no encontrada por atributo; intentando contenedor tras título")
        t = next(iter(driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Form title']")), None)
        if t:
            container = t.find_element(By.XPATH, "./ancestor::div[2]")
            cands = container.find_elements(By.XPATH, ".//*[@contenteditable='true']")
            log(f"  candidatos contenteditable en contenedor: {len(cands)}")
            for c in cands:
                log(f"    → {(c.text or '')[:40]!r}")
            if cands:
                el = cands[0]
    if el is not None:
        ok = set_field_el(el, DESC, "descripción")
        log(f"descripción: {'✅' if ok else '⚠'}")
    else:
        log("⚠ no pude localizar el campo de descripción")

    driver.quit()


def set_field_el(el, text, label):
    for a in range(8):
        try:
            ActionChains(driver).move_to_element(el).click().perform()
        except Exception:
            driver.execute_script("arguments[0].focus()", el)
        time.sleep(0.4)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(text)
        time.sleep(1.0)
        cur = (el.text or "").strip()
        log(f"  {label} intento {a+1}: {cur[:45]!r}")
        if cur == text:
            return True
        time.sleep(1.0)
    return False


if __name__ == "__main__":
    main()
