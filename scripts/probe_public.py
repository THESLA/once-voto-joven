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
    time.sleep(6)

    title = driver.execute_script("var h=document.querySelector('[role=heading]');return h?h.innerText:''")
    log(f"TÍTULO PÚBLICO: {title}")
    qs = driver.execute_script(
        "var out=[];"
        "var els=document.querySelectorAll('[role=listitem]');"
        "for(var i=0;i<els.length;i++){var t=els[i].innerText||''; if(t.trim()){out.push(t.split(String.fromCharCode(10))[0]);}}"
        "return out;"
    )
    for i, t in enumerate(qs[:20]):
        log(f"  P{i+1}: {t[:60]}")
    log(f"TOTAL items: {len(qs)}")
    driver.quit()


if __name__ == "__main__":
    main()
