import sys, time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log

EDITOR = sys.argv[1]


def main():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
    driver.get(EDITOR)
    time.sleep(8)

    cards = driver.execute_script(
        "var out = [];"
        "var tbs = document.querySelectorAll('[role=textbox][aria-label=Question]');"
        "for (var i=0;i<tbs.length;i++){"
        "  var c = tbs[i].closest('[role=listitem]') || tbs[i].parentElement;"
        "  while(c && !(c.querySelector && c.querySelector('[role=checkbox][aria-label=Required]'))){c=c.parentElement;}"
        "  var tipo='?', req='?', opts=[];"
        "  if(c){"
        "    var lb = c.querySelector('[role=listbox]'); tipo = lb ? (lb.innerText||'').trim() : 'short';"
        "    var rc = c.querySelector('[role=checkbox][aria-label=Required]'); req = rc ? rc.getAttribute('aria-checked') : '-';"
        "    var ol = c.querySelector('[role=list][aria-label=\"question options\"]');"
        "    if(ol){opts=Array.prototype.slice.call(ol.querySelectorAll('input[aria-label=\"option value\"]')).map(function(x){return x.value;});}"
        "  }"
        "  out.push({t:(tbs[i].innerText||'').trim(), ty:tipo, r:req, o:opts});"
        "}"
        "return out;"
    )
    log(f"TOTAL: {len(cards)}")
    for i, c in enumerate(cards):
        log(f"P#{i+1} [{c['ty']}] req={c['r']} :: {c['t'][:50]} :: {c['o']}")
    driver.quit()


if __name__ == "__main__":
    main()
