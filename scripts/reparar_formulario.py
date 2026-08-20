import re
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
    FORM_TITLE,
    log,
    wait_for,
    robust_click,
    question_card,
    fill_options,
    last_textbox,
)

PUBLIC_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdBV0QQWuLgxFaSod2A9yT053l-3NKQHVNR-TRUrW3lkS2V6g/viewform"

FIXES = [
    {"idx": 4, "t": "Dropdown", "opts": [str(y) for y in range(2000, 2027)]},
    {"idx": 6, "t": "Multiple choice", "opts": ["Estudiar", "Trabajar", "Ambos", "Otro"]},
    {"idx": 9, "t": "Multiple choice", "opts": ["Sí", "No"]},
    {"idx": 10, "t": "Paragraph", "opts": []},
    {"idx": 11, "t": "Multiple choice", "opts": ["Sí", "No", "No sé"]},
    {"idx": 12, "t": "Multiple choice", "opts": ["Sí", "No"]},
    {"idx": 13, "t": "Multiple choice", "opts": ["Sí", "No", "Quizás"]},
    {"idx": 14, "t": "Checkboxes", "opts": ["Sí, autorizo", "No autorizo"], "required": True},
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


def set_question_type_checked(driver, card, type_label):
    from crear_formulario_egresados import set_question_type

    return set_question_type(driver, card, type_label)


def main():
    opts = Options()
    opts.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    try:
        log("Conectando a Opera GX…")
        driver.execute_script("window.open('about:blank');")
        time.sleep(1)
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if driver.current_url.startswith("about:blank"):
                break
        log("Pestaña de automatización creada (no toco tus pestañas)")

        driver.get("https://forms.google.com")
        wait_for(
            lambda: "Recent forms" in driver.execute_script("return document.body.innerText"),
            "lista de formularios",
            25,
        )
        time.sleep(2)

        cards = driver.execute_script("""
          var out = [];
          var nodes = document.querySelectorAll('*');
          for (var i = 0; i < nodes.length; i++) {
            var el = nodes[i];
            var txt = (el.innerText || '').trim();
            if (txt === 'Untitled form' && !(el.querySelector('[data-egr-leave]'))) {
              el.setAttribute('data-egr-leave', 1);
            }
          }
          var leaves = document.querySelectorAll('[data-egr-leave]');
          leaves.forEach(function(el, idx) {
            el.setAttribute('data-egr', idx);
            var anc = el;
            var timeText = '';
            while (anc && anc !== document.body) {
              var m = (anc.innerText || '').match(/Opened(\\d+):(\\d+)\\s*([AP])M/);
              if (m) { timeText = m[1] + ':' + m[2] + (m[3] === 'P' ? ' PM' : ' AM'); break; }
              anc = anc.parentElement;
            }
            var clickable = null;
            anc = el;
            while (anc && anc !== document.body) {
              if (anc.getAttribute('role') || anc.getAttribute('tabindex') !== null ||
                  getComputedStyle(anc).cursor === 'pointer') { clickable = anc; break; }
              anc = anc.parentElement;
            }
            out.push({idx: idx, time: timeText, hasClick: !!clickable, clickIdx: idx});
          });
          return out;
        """)
        if not cards:
            raise RuntimeError("No hay borradores 'Untitled form' en la lista")

        def parse_time(t):
            m = re.match(r"(\d+):(\d+)\s*(AM|PM)", t or "")
            if not m:
                return 0
            h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
            return h * 60 + int(m.group(2))

        latest = max(cards, key=lambda c: parse_time(c["time"]))
        log(f"Borradores: {len(cards)} | click en tarjeta con '{latest['time']}'")
        leaf = driver.find_element(By.XPATH, f"//*[@data-egr='{latest['idx']}']")
        card_el = leaf
        for _ in range(6):
            if (
                card_el.get_attribute("role")
                or card_el.get_attribute("tabindex") is not None
                or driver.execute_script(
                    "return getComputedStyle(arguments[0]).cursor", card_el
                )
                == "pointer"
            ):
                break
            card_el = card_el.find_element(By.XPATH, "..")
        robust_click(driver, card_el)
        time.sleep(6)

        m = re.search(r"/d/([-\w]+)/edit", driver.current_url)
        if not m:
            raise RuntimeError(f"No entré al editor (URL: {driver.current_url[:80]})")
        draft_id = m.group(1)
        log(f"Editor abierto, draft id: {draft_id}")

        title = wait_for(lambda: last_textbox(driver, "Form title"), "título del formulario", 25)
        filled = type_editable(driver, title, FORM_TITLE)
        if filled != FORM_TITLE:
            filled = type_editable(driver, title, FORM_TITLE)
        log(f"✓ Título: {filled[:60] if filled else 'VACÍO'}")

        n_q = len(driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']"))
        log(f"Preguntas detectadas: {n_q}")

        ok = 0
        for fix in FIXES:
            try:
                card = question_card(driver, fix["idx"])
                if set_question_type_checked(driver, card, fix["t"]):
                    if fix.get("opts"):
                        fill_options(driver, card, fix["opts"])
                    if fix.get("required"):
                        req = wait_for(
                            lambda: next(
                                iter(card.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")),
                                None,
                            ),
                            "casilla requerida",
                        )
                        robust_click(driver, req)
                    ok += 1
                    log(f"  ✓ P#{fix['idx']+1}: {fix['t']}")
                else:
                    log(f"  ⚠ P#{fix['idx']+1}: tipo '{fix['t']}' NO se confirmó")
            except Exception as e:
                log(f"  ⚠ P#{fix['idx']+1}: {e}")

        qs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
        if len(qs) > 15:
            last_tb = qs[-1]
            if not (last_tb.text or "").strip():
                card = last_tb.find_element(
                    By.XPATH, "./ancestor::div[.//*[@role='checkbox' and @aria-label='Required']][1]"
                )
                del_btn = wait_for(
                    lambda: next(
                        iter(card.find_elements(By.XPATH, ".//*[@role='button' and @aria-label='Delete question']")),
                        None,
                    ),
                    "botón eliminar pregunta sobrante",
                )
                robust_click(driver, del_btn)
                log("  ✓ Pregunta sobrante eliminada")
            else:
                log("  ⚠ La pregunta extra no está vacía; no la eliminé")

        log("=" * 62)
        log(f"✅ REPARACIÓN: {ok}/{len(FIXES)} tipos corregidos")
        log(f"URL pública: {PUBLIC_URL}")
        log(f"Draft: https://docs.google.com/forms/d/{draft_id}/edit")
        log("=" * 62)
    except Exception as e:
        log(f"⛔ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
