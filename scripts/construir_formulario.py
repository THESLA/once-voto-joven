import json
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import (
    CREATE_URL,
    CHROMEDRIVER,
    OUT_FILE,
    TYPES,
    log,
    wait_for,
    wait_ready,
    last_textbox,
    fill_textbox,
    question_card,
    js_click,
    add_question,
    add_section,
)

CONFIG = r"C:\Users\RoSH\Documents\Once\scripts\formulario_config.json"


def publish(driver):
    try:
        share = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and @aria-label='Share']")), None),
            "botón Share",
            10,
        )
        js_click(driver, share)
        time.sleep(2)
        iframe = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//iframe[contains(@src,'driveshare')]")), None),
            "iframe compartir",
        )
        driver.switch_to.frame(iframe)
        pub = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//*[contains(., 'Publish the form to accept responses')]")), None),
            "enlace publicar",
        )
        js_click(driver, pub)
        time.sleep(2)
        driver.switch_to.default_content()
        log("✓ Formulario publicado (acepta respuestas)")
    except Exception as e:
        log(f"⚠ No se publicó automáticamente: {e}")


def main():
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    driver.get(CREATE_URL)
    wait_ready(driver)
    time.sleep(3)

    title = wait_for(lambda: last_textbox(driver, "Form title"), "editor del formulario", timeout=25)
    if title is None:
        log("⛔ Editor no cargó (¿sesión? inicia sesión en Opera).")
        driver.quit()
        return
    fill_textbox(driver, title, cfg["titulo"])
    log(f"✓ Título: {cfg['titulo']}")

    first_q = wait_for(lambda: last_textbox(driver, "Question"), "pregunta inicial")
    card0 = wait_for(
        lambda: first_q.find_element(By.XPATH, "./ancestor::div[.//*[@role='checkbox' and @aria-label='Required']][1]"),
        "tarjeta inicial",
    )
    js_click(driver, wait_for(
        lambda: next(iter(card0.find_elements(By.XPATH, ".//*[@role='button' and @aria-label='Delete question']")), None),
        "botón eliminar",
    ))
    log("✓ Pregunta por defecto eliminada")

    def to_q(p):
        q = {"txt": p["texto"], "t": p["tipo"]}
        if p.get("opciones"):
            q["opts"] = p["opciones"]
        if p.get("requerida"):
            q["required"] = True
        return q

    secciones = cfg["secciones"]
    for i, sec in enumerate(secciones):
        if i > 0:
            add_section(driver, sec["nombre"])
            log(f"  ✓ Sección: {sec['nombre']}")
        for p in sec["preguntas"]:
            add_question(driver, to_q(p))

    m = re.search(r"/d/([-\w]+)/edit", driver.current_url) or re.search(r"/d/([-\w]+)/", driver.current_url)
    form_id = m.group(1) if m else None

    link_el = wait_for(
        lambda: next(iter(driver.find_elements(By.XPATH, "//input[@aria-label and contains(@aria-label,'Link for sharing')]")), None),
        "enlace de respuesta",
        10,
    )
    public_url = link_el.get_attribute("value") or ""
    public_url = re.sub(r"\?usp=.*$", "", public_url)
    if not public_url and form_id:
        public_url = f"https://docs.google.com/forms/d/{form_id}/viewform"

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(public_url)

    publish(driver)
    time.sleep(3)
    log("=" * 62)
    log("✅ FORMULARIO RECONSTRUIDO")
    log(f"Editor:   https://docs.google.com/forms/d/{form_id}/edit")
    log(f"Público:  {public_url}")
    log("=" * 62)
    driver.quit()


if __name__ == "__main__":
    main()
