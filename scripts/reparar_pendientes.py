import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import (
    CHROMEDRIVER, TYPES, log, wait_for, question_card, js_click,
    set_question_type, fill_options, remove_all_options,
)

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"


def set_title(driver, el, text):
    for _ in range(6):
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
        time.sleep(0.4)
        driver.execute_script(
            "var el=arguments[0];var r=document.createRange();r.selectNodeContents(el);"
            "var s=window.getSelection();s.removeAllRanges();s.addRange(r);",
            el,
        )
        time.sleep(0.4)
        el.send_keys(text)
        time.sleep(1.0)
        if (el.text or "").strip() == text:
            return True
    return False


def opts(card):
    ol = card.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
    if not ol:
        return []
    return [i.get_attribute("value") for i in ol[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")]


def fix_title(driver, idx, text):
    card = question_card(driver, idx)
    tb = card.find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
    cur = (tb.text or "").strip()
    if cur == text:
        log(f"  P#{idx+1} título ya ok")
        return
    ok = set_title(driver, tb, text)
    log(f"{'✅' if ok else '⚠'} P#{idx+1} título → {(tb.text or '')[:45]!r}")


def fix_opts(driver, idx, lista):
    card = question_card(driver, idx)
    if opts(card) != lista:
        remove_all_options(driver, card)
        time.sleep(1.0)
        fill_options(driver, card, lista)
        time.sleep(1.5)
    log(f"P#{idx+1} opciones → {opts(card)}")


def clear_opts(driver, idx):
    card = question_card(driver, idx)
    if opts(card):
        remove_all_options(driver, card)
        time.sleep(1.0)
    log(f"P#{idx+1} opciones limpias → {opts(card)}")


def main():
    opts_opt = Options()
    opts_opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts_opt, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(10)  # dejar asentar React/autosave

    log("== P#1 Nombre completo ==")
    fix_title(driver, 0, "1. Nombre completo")
    c = question_card(driver, 0)
    r = c.find_element(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")
    if r.get_attribute("aria-checked") != "true":
        js_click(driver, r)
        time.sleep(0.8)
    log(f"  P#1 required: {r.get_attribute('aria-checked')}")

    log("== P#2 Correo electrónico ==")
    fix_title(driver, 1, "2. Correo electrónico")
    c = question_card(driver, 1)
    r = c.find_element(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")
    if r.get_attribute("aria-checked") != "true":
        js_click(driver, r)
        time.sleep(0.8)
    log(f"  P#2 required: {r.get_attribute('aria-checked')}")

    log("== P#6 opciones ==")
    fix_opts(driver, 5, ["Estudiar", "Trabajar", "Ambos", "Otro"])

    log("== P#7 quitar fantasma ==")
    clear_opts(driver, 6)

    log("== P#11 opciones ==")
    fix_opts(driver, 10, ["Sí", "No", "No sé"])

    log("fin reparar_pendientes")
    driver.quit()


if __name__ == "__main__":
    main()
