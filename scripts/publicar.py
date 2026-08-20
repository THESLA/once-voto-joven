import sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log, wait_for, js_click

EDITOR = "https://docs.google.com/forms/d/1IVcpctk2JPEnOCL9R-YFkn8RKOODIevhQIZD9hEjxqM/edit"
PUBLIC = "https://docs.google.com/forms/d/e/1FAIpQLSdBOk474lR5TCeZMHmrYXwb8HohcV9YmvoASa_2Bi6MUSpVAw/viewform"


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(6)

    try:
        # abrir diálogo Send/Share
        btn = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and (@aria-label='Send' or @aria-label='Share')]")), None),
            "botón Send/Share",
            10,
        )
        js_click(driver, btn)
        time.sleep(3)

        # cambiar a iframe
        iframe = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//iframe[contains(@src,'driveshare')]")), None),
            "iframe compartir",
            10,
        )
        driver.switch_to.frame(iframe)

        # publicar
        pub = wait_for(
            lambda: next(iter(driver.find_elements(By.XPATH, "//*[contains(., 'Publish the form to accept responses')]")), None),
            "publicar",
            8,
        )
        pub = driver.execute_script(
            "var el=arguments[0];while(el&&el!==document.body){if(el.getAttribute('role')||el.getAttribute('jsaction')||getComputedStyle(el).cursor==='pointer')return el;el=el.parentElement;}return arguments[0];",
            pub,
        )
        js_click(driver, pub)
        time.sleep(2)
        log("✓ Publicado: acepta respuestas")
        driver.switch_to.default_content()
    except Exception as e:
        log(f"⚠ Publicación: {e}")
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

    # verificar viewform
    time.sleep(3)
    driver.get(PUBLIC)
    time.sleep(6)
    try:
        title = driver.execute_script("var h=document.querySelector('[role=heading]');return h?h.innerText:''")
        qs = driver.execute_script(
            "var out=[];var els=document.querySelectorAll('[role=listitem]');"
            "for(var i=0;i<els.length;i++){var t=(els[i].innerText||'').trim();if(t){out.push(t.split(String.fromCharCode(10))[0]);}}"
            "return out;"
        )
        log(f"PÚBLICO título: {title}")
        log(f"PÚBLICO count: {len(qs)}")
        for i, t in enumerate(qs[:16]):
            log(f"  Q{i+1}: {t[:55]}")
    except Exception as e:
        log(f"⚠ verificación pública: {e}")
    driver.quit()


if __name__ == "__main__":
    main()
