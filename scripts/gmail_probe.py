import sys, time
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from crear_formulario_egresados import CHROMEDRIVER, log

TO = "sanluistrabajosestudiantes@gmail.com"
SUBJECT = "Actividad: Encuesta de estudiantes de grado once - Colegio San Luis"
BODY = "Cordial saludo"
url = ("https://mail.google.com/mail/u/0/?view=cm&fs=1&tf=1"
       f"&to={quote(TO)}&su={quote(SUBJECT)}&body={quote(BODY)}")

opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))
log("pestañas: " + str(len(driver.window_handles)))
driver.switch_to.window(driver.window_handles[0])
driver.get(url)
time.sleep(8)
log("url: " + driver.current_url[:80])
log("titulo: " + driver.title[:60])

txt = driver.find_elements(By.CSS_SELECTOR, "textarea[name='to']")
log("textarea[name=to]: " + str(len(txt)))
areas = driver.find_elements(By.CSS_SELECTOR, "textarea")
log("total textareas: " + str(len(areas)))
for i in areas[:6]:
    log("  textarea name={} aria={} val={}".format(i.get_attribute('name'), i.get_attribute('aria-label'), (i.get_attribute('value') or '')[:40]))
recips = driver.find_elements(By.XPATH, "//*[@aria-label[contains(.,'Para') or contains(.,'To') or contains(.,'Destinatario')]]")
log("elementos aria Para/To/Destinatario: " + str(len(recips)))
for i in recips[:5]:
    log("  tag={} name={} aria={} val={}".format(i.tag_name, i.get_attribute('name'), i.get_attribute('aria-label'), (i.get_attribute('value') or '')[:40]))
inputs = driver.find_elements(By.CSS_SELECTOR, "input[name]")
log("inputs con name: " + str(len(inputs)) + " | names: " + str([i.get_attribute('name') for i in inputs][:10]))
labels = driver.find_elements(By.XPATH, "//input[@aria-label or @placeholder]")
for i in inputs:
    log("  input name={} tipo={} aria={}".format(i.get_attribute('name'), i.get_attribute('type'), i.get_attribute('aria-label')))
# cuerpo
body = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
log("cuerpos editables: " + str(len(body)))
dlg = driver.find_elements(By.CSS_SELECTOR, "div[role='dialog']")
log("dialogos: " + str(len(dlg)))
if dlg:
    log("  texto dialogo: " + (dlg[0].text[:150]).replace("\n", " | "))
driver.quit()