import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from crear_formulario_egresados import CHROMEDRIVER, log, question_card, wait_for

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"

tb = lambda idx: question_card(idx_driver, idx).find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
ins = lambda idx: question_card(idx_driver, idx).find_elements(By.XPATH, ".//input[@aria-label='option value']")


def opts(idx):
    ol = question_card(idx_driver, idx).find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
    if not ol:
        return []
    return [i.get_attribute("value") for i in ol[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")]


def set_title(idx, text):
    for _ in range(8):
        e = tb(idx)
        driver.execute_script("window.scrollTo(0, arguments[0]);", e.location['y'] - 160)
        time.sleep(0.4)
        ActionChains(driver).move_to_element(e).click().perform()
        time.sleep(0.3)
        e = tb(idx)  # re-query tras clic (React pudo reemplazar)
        e.send_keys(Keys.CONTROL, "a")
        e.send_keys(text)
        time.sleep(0.8)
        cur = (tb(idx).text or "").strip()  # re-query para verificar
        if cur == text:
            return True
    return (tb(idx).text or "").strip()


def set_opt(idx, target):
    # asegurar cantidad
    for _ in range(max(0, len(target) - len(ins(idx)))):
        card = question_card(idx_driver, idx)
        add = wait_for(lambda: next(iter(card.find_elements(By.XPATH, ".//*[normalize-space(.)='Add option']")), None), "add option")
        driver.execute_script(
            "var el=arguments[0];while(el&&el!==document.body){if(el.getAttribute('jsaction')||el.getAttribute('role')||getComputedStyle(el).cursor==='pointer')return el;el=el.parentElement;}return arguments[0];",
            add,
        ).click()
        time.sleep(0.8)
    for i, val in enumerate(target):
        for _ in range(6):
            arr = ins(idx)
            if i >= len(arr):
                break
            inp = arr[i]
            ActionChains(driver).move_to_element(inp).click().perform()
            time.sleep(0.3)
            arr = ins(idx)
            if i >= len(arr):
                break
            inp = arr[i]
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(val)
            time.sleep(0.7)
            after = (ins(idx)[i].get_attribute("value") or "").strip() if i < len(ins(idx)) else ""
            if after == val:
                break
    time.sleep(1.0)
    return opts(idx)


def clear_opts(idx):
    for _ in range(30):
        card = question_card(idx_driver, idx)
        btn = next(iter(card.find_elements(By.XPATH, ".//*[@aria-label='Remove option']")), None)
        if not btn:
            break
        btn.click()
        time.sleep(0.5)
    return opts(idx)


def main():
    opts_opt = Options()
    opts_opt.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    global driver, idx_driver
    idx_driver = webdriver.Chrome(options=opts_opt, service=Service(CHROMEDRIVER))
    driver = idx_driver
    driver.get(EDITOR)
    time.sleep(12)

    log(f"P#1 título (objetivo '1. Nombre completo') → {set_title(0, '1. Nombre completo')!r}")
    log(f"P#7 tras limpiar → {clear_opts(6)}")
    log(f"P#6 opciones → {set_opt(5, ['Estudiar','Trabajar','Ambos','Otro'])}")
    log(f"P#11 opciones → {set_opt(10, ['Sí','No','No sé'])}")
    log("fin fix_final2")
    driver.quit()


if __name__ == "__main__":
    main()