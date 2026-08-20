import sys, time
sys.path.insert(0, r"C:\Users\RoSH\Documents\Once\scripts")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from crear_formulario_egresados import CHROMEDRIVER, log

DRAFT = "https://docs.google.com/forms/d/1BYfmwRgiFp03yyqh_E-E07WbRxq8F0maFvJvuBLt4_I/edit"
TEXT = "15. Autorizo el tratamiento de mis datos personales conforme a la Ley 1581 de 2012"

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
    time.sleep(7)
    for attempt in range(3):
        qs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
        tb = qs[14]
        driver.execute_script("""
          arguments[0].focus();
          var range = document.createRange();
          range.selectNodeContents(arguments[0]);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
        """, tb)
        time.sleep(0.3)
        tb.send_keys(TEXT)
        time.sleep(0.6)
        filled = (tb.text or "").strip()
        log(f"intento {attempt+1}: {filled[:45]!r}")
        if filled == TEXT:
            break
    log("✅ P#15: " + (filled if filled == TEXT else "⚠ FALLÓ"))
finally:
    driver.quit()
