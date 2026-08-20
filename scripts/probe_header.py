import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log

PUBLIC = "https://docs.google.com/forms/d/e/1FAIpQLSdBOk474lR5TCeZMHmrYXwb8HohcV9YmvoASa_2Bi6MUSpVAw/viewform"


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(PUBLIC)
    time.sleep(7)
    data = driver.execute_script(
        "var h=document.querySelector('[role=heading]');"
        "var head = h ? h.closest('div[class]').parentElement : null;"
        "var txt = head ? head.innerText : '';"
        "return {title: h?h.innerText:'', head: txt.slice(0,600)};"
    )
    log(f"TÍTULO: {data['title']}")
    log("ENCABEZADO:")
    for line in data['head'].splitlines():
        if line.strip():
            log(f"  | {line[:80]}")
    driver.quit()


if __name__ == "__main__":
    main()
