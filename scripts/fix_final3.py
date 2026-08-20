import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log, question_card, wait_for, robust_click

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"


def opts(idx):
    ol = question_card(driver, idx).find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
    return [i.get_attribute("value") for i in ol[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")] if ol else []


def set_title(idx, text, debug=False):
    for _ in range(8):
        e = question_card(driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
        driver.execute_script("window.scrollTo(0, arguments[0]);", e.location['y'] - 160)
        time.sleep(0.4)
        try:
            ActionChains(driver).move_to_element(e).click().perform()
        except Exception:
            driver.execute_script("arguments[0].focus()", e)
        time.sleep(0.3)
        e = question_card(driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
        e.send_keys(Keys.CONTROL, "a")
        e.send_keys(text)
        time.sleep(0.9)
        cur = (question_card(driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']").text or "").strip()
        if cur == text:
            return cur
        time.sleep(0.5)
        if debug and _ == 0:
            h = question_card(driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']").get_attribute("outerHTML")
            log(f"  [debug P#1] outerHTML len={len(h)} tag={h[:120]}")
    return (question_card(driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']").text or "").strip()


def set_opt(idx, target):
    for _ in range(max(0, len(target) - len(opts(idx)))):
        card = question_card(driver, idx)
        add = wait_for(lambda: next(iter(card.find_elements(By.XPATH, ".//*[normalize-space(.)='Add option']")), None), "add")
        driver.execute_script(
            "var el=arguments[0];while(el&&el!==document.body){if(el.getAttribute('jsaction')||el.getAttribute('role')||getComputedStyle(el).cursor==='pointer')return el;el=el.parentElement;}return arguments[0];",
            add,
        ).click()
        time.sleep(0.8)
    for i, val in enumerate(target):
        for _ in range(6):
            arr = question_card(driver, idx).find_elements(By.XPATH, ".//input[@aria-label='option value']")
            if i >= len(arr):
                break
            inp = arr[i]
            ActionChains(driver).move_to_element(inp).click().perform()
            time.sleep(0.3)
            arr = question_card(driver, idx).find_elements(By.XPATH, ".//input[@aria-label='option value']")
            inp = arr[i]
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(val)
            time.sleep(0.7)
            arr = question_card(driver, idx).find_elements(By.XPATH, ".//input[@aria-label='option value']")
            if i < len(arr) and (arr[i].get_attribute("value") or "").strip() == val:
                break
    time.sleep(1.0)
    return opts(idx)


def clear_opts(idx):
    for _ in range(40):
        card = question_card(driver, idx)
        btn = next(iter(card.find_elements(By.XPATH, ".//*[@aria-label='Remove option']")), None)
        if not btn:
            break
        robust_click(driver, btn)
        time.sleep(0.6)
    return opts(idx)


def main():
    opts_opt = Options()
    opts_opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    global driver
    driver = webdriver.Chrome(options=opts_opt, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(12)

    try:
        log(f"P#1 título → {set_title(0, '1. Nombre completo', debug=True)!r}")
    except Exception as ex:
        log(f"P#1 error: {ex}")
    try:
        log(f"P#7 limpiar → {clear_opts(6)}")
    except Exception as ex:
        log(f"P#7 error: {ex}")
    try:
        log(f"P#6 opciones → {set_opt(5, ['Estudiar','Trabajar','Ambos','Otro'])}")
    except Exception as ex:
        log(f"P#6 error: {ex}")
    try:
        log(f"P#11 opciones → {set_opt(10, ['Sí','No','No sé'])}")
    except Exception as ex:
        log(f"P#11 error: {ex}")
    log("fin fix_final3")
    driver.quit()


if __name__ == "__main__":
    main()