import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log, question_card, set_question_type, wait_for

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"


def opts(card):
    ol = card.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
    if not ol:
        return []
    return [i.get_attribute("value") for i in ol[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")]


def real_set(el, text):
    for _ in range(6):
        try:
            ActionChains(driver).move_to_element(el).click().perform()
        except Exception:
            el.click()
        time.sleep(0.25)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(text)
        time.sleep(0.7)
        if (el.get_attribute("value") or "").strip() == text:
            return True
        time.sleep(0.5)
    return False


def set_title_real(driver, el, text):
    for _ in range(6):
        driver.execute_script("window.scrollTo(0, arguments[0]);", el.location['y'] - 150)
        time.sleep(0.5)
        try:
            ActionChains(driver).move_to_element(el).click().perform()
        except Exception:
            el.click()
        time.sleep(0.3)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(text)
        time.sleep(0.9)
        if (el.text or "").strip() == text:
            return True
        time.sleep(0.5)
    return False


def overwrite_opts(driver, idx, target):
    card = question_card(driver, idx)
    ins_all = lambda: card.find_elements(By.XPATH, ".//input[@aria-label='option value']")
    # agregar tantos como falten
    for _ in range(len(target) - len(ins_all())):
        add_btn = wait_for(lambda: next(iter(card.find_elements(By.XPATH, ".//*[normalize-space(.)='Add option']")), None), "add option")
        driver.execute_script(
            "var el=arguments[0];while(el&&el!==document.body){if(el.getAttribute('jsaction')||el.getAttribute('role')||getComputedStyle(el).cursor==='pointer')return el;el=el.parentElement;}return arguments[0];",
            add_btn,
        ).click()
        time.sleep(0.8)
    for i, val in enumerate(target):
        try:
            inp = ins_all()[i]
        except IndexError:
            break
        if (inp.get_attribute("value") or "").strip() != val:
            real_set(inp, val)
    time.sleep(1.0)
    final = opts(card)
    log(f"P#{idx+1} opciones → {final} (objetivo {target})")


def main():
    opts_opt = Options()
    opts_opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    global driver
    driver = webdriver.Chrome(options=opts_opt, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(12)

    # P#1 título
    tb = question_card(driver, 0).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
    ok = set_title_real(driver, tb, "1. Nombre completo")
    log(f"{'✅' if ok else '⚠'} P#1 título → {(tb.text or '')[:45]!r}")

    # P#7 tipo short (quitar opciones) — está antes de P6 en orden? no, P7 idx6
    card7 = question_card(driver, 6)
    if opts(card7):
        set_question_type(driver, card7, "Short answer")
        time.sleep(1.0)
    log(f"P#7 opciones tras Short → {opts(question_card(driver, 6))}")

    # opciones in-place
    overwrite_opts(driver, 5, ["Estudiar", "Trabajar", "Ambos", "Otro"])
    overwrite_opts(driver, 10, ["Sí", "No", "No sé"])

    log("fin fix_final")
    driver.quit()


if __name__ == "__main__":
    main()