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
    question_card,
    set_question_type,
    fill_options,
    last_textbox,
)

DRAFT = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"

FORM_TITLE = "Registro de Estudiantes – Colegio San Luis"

SECTION_TITLES = [
    "SECCIÓN 2 — Planes después del colegio",
    "SECCIÓN 3 — Tu conexión con el colegio",
    "SECCIÓN 4 — Participación",
    "SECCIÓN 5 — Consentimiento (obligatoria)",
]

GRADES = [
    "Grado 6°", "Grado 7°", "Grado 8°", "Grado 9°",
    "Grado 10°", "Grado 11°", "Ya no estudio en el colegio",
]

Q_TITLES = {
    4: "5. ¿En qué grado estás actualmente?",
    6: "7. ¿Qué piensas hacer al terminar el colegio?",
    7: "8. Si piensas estudiar: ¿qué carrera te interesa?",
    8: "9. Si piensas trabajar: ¿en qué te gustaría trabajar?",
    9: "10. ¿Conoces a otros compañeros de grado once que no hayan diligenciado este registro?",
    10: "11. Si respondiste sí, ¿nos compartes sus datos? (nombre, correo o WhatsApp)",
    11: "12. ¿Tienes familiares que estudien o hayan estudiado en el colegio (padres, tíos, hermanos)?",
    12: "13. ¿Te gustaría participar en las actividades de tu promoción y del colegio?",
    13: "14. ¿Te gustaría ser vocero/a de tu curso y ayudar a organizar las actividades de grado once?",
}


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
        wait_for(lambda: last_textbox(driver, "Form title"), "editor", 30)
        time.sleep(2)

        ft = last_textbox(driver, "Form title")
        filled = type_editable(driver, ft, FORM_TITLE)
        log(f"{'✅' if filled == FORM_TITLE else '⚠'} Título: {filled[:50]}")

        secs = driver.find_elements(By.XPATH, "//*[@role='textbox' and contains(@aria-label, 'Section')]")
        for i, tb in enumerate(secs[:4]):
            expected = SECTION_TITLES[i]
            ok = False
            for _ in range(3):
                filled = type_editable(driver, tb, expected)
                if filled == expected:
                    ok = True
                    break
            log(f"{'✅' if ok else '⚠'} Sección {i+2}: {expected if ok else filled[:40]!r}")

        for qidx, text in Q_TITLES.items():
            ok = False
            for _ in range(3):
                qs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
                filled = type_editable(driver, qs[qidx], text)
                if filled == text:
                    ok = True
                    break
            log(f"{'✅' if ok else '⚠'} P#{qidx+1}: {text[:55]}")

        card = question_card(driver, 4)
        set_question_type(driver, card, "Short answer")
        log("  → dropdown reiniciado (Short answer)")
        set_question_type(driver, card, "Dropdown")
        fill_options(driver, card, GRADES)
        log("✅ P#5 opciones: " + ", ".join(GRADES[:4]) + "…")

        log("=" * 62)
        log("CORRECCIÓN FINALIZADA — revisa el editor para confirmar")
        log("=" * 62)
    except Exception as e:
        log(f"⛔ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
