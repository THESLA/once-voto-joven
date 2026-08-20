import sys, time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log, js_click, robust_click, question_card, wait_for

EDITOR_URL = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"


def titles(driver):
    return driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")


def type_text(driver, el, text):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
    time.sleep(0.2)
    driver.execute_script(
        "var el = arguments[0];"
        "var r = document.createRange(); r.selectNodeContents(el);"
        "var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);",
        el,
    )
    time.sleep(0.2)
    el.send_keys(text)
    time.sleep(0.6)
    return (el.text or "").strip()


def main():
    texto = sys.argv[1]
    required = len(sys.argv) > 2 and sys.argv[2].lower() in ("1", "true", "si", "sí")

    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR_URL)
    time.sleep(4)

    before = len(titles(driver))

    add_btn = wait_for(
        lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and @aria-label='Add question']")), None),
        "Add question",
    )
    add_btn = driver.execute_script(
        "var el = arguments[0];"
        "while (el && el !== document.body) {"
        "  if (el.getAttribute('jsaction') || el.getAttribute('role') || getComputedStyle(el).cursor === 'pointer') return el;"
        "  el = el.parentElement;"
        "}"
        "return arguments[0];",
        add_btn,
    )
    js_click(driver, add_btn)
    time.sleep(3)

    after_add = len(titles(driver))
    card = question_card(driver, after_add - 1)
    tb = card.find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
    filled = type_text(driver, tb, texto)
    log(f"pregunta nueva titulo: {filled!r}")

    if required:
        req = wait_for(lambda: next(iter(card.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")), None), "Required")
        if req.get_attribute("aria-checked") != "true":
            robust_click(driver, req)
            time.sleep(1)
        log(f"required: {req.get_attribute('aria-checked')}")

    # mover al inicio (arriba de la primera pregunta)
    handle = wait_for(lambda: next(iter(card.find_elements(By.XPATH, ".//*[@aria-label='Drag to move']")), None), "asidero drag")
    target = titles(driver)[0]
    ActionChains(driver).drag_and_drop(handle, target).perform()
    time.sleep(3)

    tbs = titles(driver)
    log(f"preguntas: {len(tbs)} (antes={before}, tras-add={after_add})")
    for i in range(min(6, len(tbs))):
        log(f"  P#{i+1}: {(tbs[i].text or '')[:45]}")
    driver.quit()


if __name__ == "__main__":
    main()
