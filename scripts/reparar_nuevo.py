import json, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from crear_formulario_egresados import (
    CHROMEDRIVER, TYPES, log, wait_for, question_card, js_click,
    set_question_type, fill_options, remove_all_options,
)

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"
CONFIG = r"C:\Users\RoSH\Documents\Once\scripts\formulario_config.json"


def flatten(cfg):
    out = []
    for sec in cfg["secciones"]:
        for p in sec["preguntas"]:
            out.append({
                "titulo": p["texto"],
                "tipo": p["tipo"],
                "opts": p.get("opciones", []),
                "req": p.get("requerida", False),
            })
    return out


def set_title(driver, el, text):
    for _ in range(4):
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
        time.sleep(0.3)
        driver.execute_script(
            "var el=arguments[0];var r=document.createRange();r.selectNodeContents(el);"
            "var s=window.getSelection();s.removeAllRanges();s.addRange(r);",
            el,
        )
        time.sleep(0.3)
        el.send_keys(text)
        time.sleep(0.8)
        if (el.text or "").strip() == text:
            return True
    return False


def card_opts(card):
    ol = card.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")
    if not ol:
        return []
    return [i.get_attribute("value") for i in ol[0].find_elements(By.XPATH, ".//input[@aria-label='option value']")]


def main():
    items = flatten(json.load(open(CONFIG, encoding="utf-8")))
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(7)

    tbs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
    n = min(len(tbs), len(items))
    for i in range(n):
        item = items[i]
        card = question_card(driver, i)
        tb = card.find_element(By.XPATH, ".//*[@role='textbox' and @aria-label='Question']")
        cur = (tb.text or "").strip()

        # tipo
        has_opts = bool(card.find_elements(By.XPATH, ".//input[@aria-label='option value']"))
        if item["opts"] and item["tipo"] != "short":
            if not has_opts or len(card_opts(card)) < len(item["opts"]):
                set_question_type(driver, card, TYPES[item["tipo"]])
                time.sleep(1.0)

        # opciones
        if item["opts"]:
            if card_opts(card) != item["opts"]:
                remove_all_options(driver, card)
                time.sleep(0.8)
                fill_options(driver, card, item["opts"])
            time.sleep(1.0)
        else:
            if has_opts:
                set_question_type(driver, card, TYPES[item["tipo"]])
                time.sleep(0.8)
                remove_all_options(driver, card)
                time.sleep(0.5)

        # título
        if cur != item["titulo"]:
            set_title(driver, tb, item["titulo"])
            time.sleep(1.0)

        # requerida
        req = card.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")
        checked = req[0].get_attribute("aria-checked") == "true" if req else False
        if req and item["req"] != checked:
            js_click(driver, req[0])
            time.sleep(0.8)

        final_title = (tb.text or "").strip()
        final_opts = card_opts(card)
        req_f = req[0].get_attribute("aria-checked") if req else "-"
        ok = final_title == item["titulo"] and final_opts == item["opts"] and (not item["req"] or req_f == "true")
        log(f"{'✅' if ok else '⚠'} P#{i+1} :: {final_title[:45]} :: {final_opts} req={req_f}")

    log("fin reparar_nuevo")
    driver.quit()


if __name__ == "__main__":
    main()
