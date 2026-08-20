import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import (
    CHROMEDRIVER,
    log,
    wait_for,
    question_card,
    fill_options,
    remove_all_options,
)

EDITOR_URL = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"

GRADES = [
    "Grado 6°",
    "Grado 7°",
    "Grado 8°",
    "Grado 9°",
    "Grado 10°",
    "Grado 11°",
    "Ya no estudio en el colegio",
]

FIXES = [
    (4, GRADES, "P#5 grado actual"),
    (6, ["Estudiar", "Trabajar", "Ambos", "Otro"], "P#7 futuro"),
    (11, ["Sí", "No", "No sé"], "P#12 voto"),
    (13, ["Sí", "No", "Quizás"], "P#14 intención"),
    (14, ["Sí, autorizo", "No autorizo"], "P#15 datos"),
]


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    driver.get(EDITOR_URL)
    time.sleep(4)

    for qidx, options, label in FIXES:
        card = question_card(driver, qidx)
        remove_all_options(driver, card)
        fill_options(driver, card, options)
        time.sleep(1.0)
        list_el = wait_for(
            lambda c=card: next(
                iter(c.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")),
                None,
            ),
            f"lista de {label}",
        )
        values = [i.get_attribute("value") for i in list_el.find_elements(By.XPATH, ".//input[@aria-label='option value']")]
        ok = values == options
        log(f"{'✅' if ok else '⚠'} {label}: {values}")
        time.sleep(2.0)

    card15 = question_card(driver, 14)
    req = wait_for(lambda: next(iter(card15.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")), None), "checkbox requerida P#15")
    checked = req.get_attribute("aria-checked")
    log(f"P#15 required aria-checked: {checked}")
    if checked != "true":
        from crear_formulario_egresados import robust_click

        robust_click(driver, req)
        time.sleep(1.0)
        log(f"P#15 required tras clic: {req.get_attribute('aria-checked')}")

    log("fin arreglar_opciones")
    driver.quit()


if __name__ == "__main__":
    main()
