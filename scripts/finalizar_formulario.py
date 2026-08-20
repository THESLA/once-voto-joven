import sys
import time

sys.path.insert(0, r"C:\Users\RoSH\Documents\Once\scripts")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import (
    CHROMEDRIVER,
    log,
    wait_for,
    robust_click,
)

DRAFT = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"
PUBLIC_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdBV0QQWuLgxFaSod2A9yT053l-3NKQHVNR-TRUrW3lkS2V6g/viewform"

SECTION_TITLES = [
    "SECCIÓN 1 — Tus datos",
    "SECCIÓN 2 — Después del colegio",
    "SECCIÓN 3 — Red de egresados",
    "SECCIÓN 4 — Participación",
    "SECCIÓN 5 — Consentimiento (obligatoria)",
]


def type_editable(driver, el, text):
    try:
        ActionChains(driver).move_to_element(el).click().perform()
    except Exception:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
    time.sleep(0.2)
    el.send_keys(Keys.CONTROL, "a")
    el.send_keys(text)
    time.sleep(0.5)
    return (el.text or "").strip()


def main():
    opts = Options()
    opts.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    try:
        log("Conectando a Opera GX…")
        driver.execute_script("window.open('about:blank');")
        time.sleep(1)
        for h in driver.window_handles:
            driver.switch_to.window(h)
            if driver.current_url.startswith("about:blank"):
                break
        log("Pestaña de automatización lista")

        driver.get(DRAFT)
        wait_for(lambda: last_textbox(driver, "Form title"), "editor", 30)
        time.sleep(2)

        secs = driver.find_elements(
            By.XPATH, "//*[@role='textbox' and contains(@aria-label, 'Section')]"
        )
        log(f"Títulos de sección detectados: {len(secs)}")
        for i, tb in enumerate(secs[:5]):
            expected = SECTION_TITLES[i]
            for attempt in range(3):
                filled = type_editable(driver, tb, expected)
                if filled == expected:
                    break
            if filled == expected:
                log(f"  ✓ Sección {i+1}: {expected}")
            else:
                log(f"  ⚠ Sección {i+1}: quedó {filled[:40]!r}")

        share = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and @aria-label='Share']")), None),
            "botón Share",
        )
        robust_click(driver, share)
        time.sleep(5)

        frame = None
        for f in driver.find_elements(By.TAG_NAME, "iframe"):
            if "driveshare" in (f.get_attribute("src") or ""):
                frame = f
                break
        if frame is None:
            raise RuntimeError("No abrió el diálogo de compartir")
        driver.switch_to.frame(frame)
        publish_link = wait_for(
            lambda: next(
                iter(
                    driver.find_elements(
                        By.XPATH, "//*[contains(., 'Publish the form to accept responses')]"
                    )
                ),
                None,
            ),
            "enlace publicar",
            10,
        )
        robust_click(driver, publish_link)
        log("✓ Publicar pulsado")
        driver.switch_to.default_content()
        time.sleep(3)

        driver.execute_script("window.open(arguments[0]);", PUBLIC_URL)
        time.sleep(4)
        for h in driver.window_handles:
            driver.switch_to.window(h)
            if "viewform" in driver.current_url:
                break
        body = driver.execute_script("return document.body.innerText")
        if "not published" in body:
            log("⛔ El formulario sigue sin publicar")
        else:
            log("✅ FORMULARIO PUBLICADO")
            title = driver.execute_script(
                "var h = document.querySelector('[role=heading]'); return h ? h.innerText : ''"
            )
            log(f"Título público: {title[:70]}")
            log(f"URL pública: {PUBLIC_URL}")

        with open("formulario_egresados_url.txt", "w", encoding="utf-8") as fh:
            fh.write(PUBLIC_URL)
        log("(URL guardada en formulario_egresados_url.txt)")
    except Exception as e:
        log(f"⛔ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
