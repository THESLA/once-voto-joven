import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

HOME_URL = "https://forms.google.com"
CREATE_URL = "https://docs.google.com/forms/create"
CHROMEDRIVER = r"C:\Users\RoSH\AppData\Local\Temp\opencode\drivers\chromedriver-win64\chromedriver.exe"
OUT_FILE = "formulario_egresados_url.txt"
LOGIN_TIMEOUT = 600
STEP_TIMEOUT = 30

FORM_TITLE = "Registro de Egresados – Colegio San Luis"

SECTIONS = [
    ("SECCIÓN 1 — Tus datos", [
        {"t": "short", "txt": "1. Nombre completo"},
        {"t": "short", "txt": "2. Correo electrónico"},
        {"t": "short", "txt": "3. Teléfono / WhatsApp (número)"},
        {"t": "short", "txt": "4. Ciudad donde vives actualmente"},
        {"t": "dropdown", "txt": "5. ¿En qué año te graduaste del colegio?", "opts": [str(y) for y in range(2000, 2027)]},
        {"t": "short", "txt": "6. ¿Cómo se llamó tu promoción (o quintos)? (opcional)"},
    ]),
    ("SECCIÓN 2 — Después del colegio", [
        {"t": "multiple", "txt": "7. ¿Qué hiciste al graduarte?", "opts": ["Estudiar", "Trabajar", "Ambos", "Otro"]},
        {"t": "short", "txt": "8. Si estudiaste: ¿dónde y qué carrera?"},
        {"t": "short", "txt": "9. Si trabajas: ¿en qué trabajas o profesión?"},
    ]),
    ("SECCIÓN 3 — Red de egresados", [
        {"t": "multiple", "txt": "10. ¿Conoces a otros egresados que no hayan diligenciado este registro?", "opts": ["Sí", "No"]},
        {"t": "paragraph", "txt": "11. Si respondiste sí, ¿nos compartes sus datos? (nombre, correo o WhatsApp)"},
        {"t": "multiple", "txt": "12. ¿Tienes familiares que también sean egresados del colegio (padres, tíos, hermanos)?", "opts": ["Sí", "No", "No sé"]},
    ]),
    ("SECCIÓN 4 — Participación", [
        {"t": "multiple", "txt": "13. ¿Te gustaría participar en actividades de la red de egresados?", "opts": ["Sí", "No"]},
        {"t": "multiple", "txt": "14. ¿Te interesaría ser mentor/a o venir a hablar con los estudiantes de grado once sobre lo que haces?", "opts": ["Sí", "No", "Quizás"]},
    ]),
    ("SECCIÓN 5 — Consentimiento (obligatoria)", [
        {"t": "checkbox", "txt": "15. Autorizo el tratamiento de mis datos personales conforme a la Ley 1581 de 2012", "opts": ["Sí, autorizo", "No autorizo"], "required": True},
    ]),
]

TYPES = {
    "short": "Short answer",
    "paragraph": "Paragraph",
    "multiple": "Multiple choice",
    "checkbox": "Checkboxes",
    "dropdown": "Dropdown",
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def wait_for(fn, what, timeout=STEP_TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            el = fn()
            if el is not None:
                return el
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"No se encontró: {what}")


def js_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.1)
    driver.execute_script("arguments[0].click();", el)


def fill_editable(driver, el, text):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", el)
    time.sleep(0.1)
    el.send_keys(Keys.CONTROL, "a")
    el.send_keys(text)


def js_set_input(driver, el, text):
    driver.execute_script(
        "var el = arguments[0];"
        "var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
        "setter.call(el, arguments[1]);"
        "el.dispatchEvent(new Event('input', {bubbles:true}));"
        "el.dispatchEvent(new Event('change', {bubbles:true}));",
        el,
        text,
    )


def wait_ready(driver, timeout=STEP_TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if driver.execute_script("return document.readyState") == "complete":
            return
        time.sleep(0.5)


def last_textbox(driver, aria):
    els = driver.find_elements(By.XPATH, f"//*[@role='textbox' and @aria-label='{aria}']")
    return els[-1] if els else None


def fill_textbox(driver, el, text):
    fill_editable(driver, el, text)


def question_card(driver, index=-1):
    qs = driver.find_elements(By.XPATH, "//*[@role='textbox' and @aria-label='Question']")
    tb = qs[index]
    return wait_for(
        lambda: tb.find_element(By.XPATH, "./ancestor::div[.//*[@role='checkbox' and @aria-label='Required']][1]"),
        "tarjeta de pregunta",
    )


def robust_click(driver, el):
    driver.execute_script(
        "var el = arguments[0];"
        "el.scrollIntoView({block:'center'});"
        "el.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true, cancelable:true, pointerType:'mouse'}));"
        "el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true, cancelable:true}));"
        "el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true, cancelable:true}));"
        "el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));",
        el,
    )


def set_question_type(driver, card, type_label):
    listbox = wait_for(
        lambda: next(iter(card.find_elements(By.XPATH, ".//*[@role='listbox' and @aria-label='Question types']")), None),
        "selector de tipo",
    )
    for attempt in range(4):
        driver.execute_script("arguments[0].click();", listbox)
        time.sleep(0.4)
        option = wait_for(
            lambda: next(
                iter(driver.find_elements(By.XPATH, f"//*[@role='option'][contains(., '{type_label}')]")),
                None,
            ),
            f"tipo '{type_label}'",
            4,
        )
        driver.execute_script("arguments[0].click();", option)
        time.sleep(1.0)
        if type_label == "Paragraph":
            marker = card.find_elements(By.TAG_NAME, "textarea")
        else:
            marker = card.find_elements(By.XPATH, ".//input[@aria-label='option value']")
        if marker:
            return True
    n_opts = len(driver.find_elements(By.XPATH, "//*[@role='option']"))
    log(f"  ⚠ no se aplicó '{type_label}' (options visibles: {n_opts})")
    return False


def fill_options(driver, card, opts):
    def fresh_list():
        return wait_for(
            lambda: next(
                iter(card.find_elements(By.XPATH, ".//*[@role='list' and @aria-label='question options']")),
                None,
            ),
            "lista de opciones",
        )

    options_list = fresh_list()
    inputs = lambda: options_list.find_elements(By.XPATH, ".//input[@aria-label='option value']")

    def set_at(idx, text):
        for attempt in range(4):
            try:
                inp = inputs()[idx]
            except IndexError:
                return False
            js_click(driver, inp)
            time.sleep(0.15)
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(text)
            time.sleep(0.4)
            if (inp.get_attribute("value") or "").strip() == text:
                return True
        return False

    ok = set_at(0, opts[0])
    time.sleep(0.2)
    for i, opt_text in enumerate(opts[1:], start=1):
        options_list = fresh_list()
        add_btn = wait_for(
            lambda: next(
                iter(card.find_elements(By.XPATH, ".//*[normalize-space(.)='Add option']")),
                None,
            ),
            "botón agregar opción",
            8,
        )
        add_btn = driver.execute_script(
            "var el = arguments[0];"
            "while (el && el !== document.body) {"
            "  if (el.getAttribute('jsaction') || el.getAttribute('role') || getComputedStyle(el).cursor === 'pointer') return el;"
            "  el = el.parentElement;"
            "}"
            "return arguments[0];",
            add_btn,
        )
        js_click(driver, add_btn)
        time.sleep(0.6)
        if not set_at(i, opt_text):
            log(f"  ⚠ opción '{opt_text[:20]}' no guardada (pos {i})")
        time.sleep(0.2)


def remove_all_options(driver, card):
    guard = 0
    while guard < 60:
        btns = card.find_elements(By.XPATH, ".//*[@aria-label='Remove option']")
        if not btns:
            return
        js_click(driver, btns[0])
        time.sleep(0.4)
        guard += 1


def add_question(driver, q):
    add_btn = wait_for(
        lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and @aria-label='Add question']")), None),
        "botón agregar pregunta",
    )
    js_click(driver, add_btn)
    time.sleep(0.8)
    tb = wait_for(
        lambda: last_textbox(driver, "Question"),
        "título de pregunta nueva",
    )
    fill_textbox(driver, tb, q["txt"])
    card = question_card(driver, -1)
    if q["t"] != "short":
        set_question_type(driver, card, TYPES[q["t"]])
    if q.get("opts"):
        fill_options(driver, card, q["opts"])
    if q.get("required"):
        req = wait_for(
            lambda: next(iter(card.find_elements(By.XPATH, ".//*[@role='checkbox' and @aria-label='Required']")), None),
            "casilla requerida",
        )
        js_click(driver, req)
    log(f"  ✓ {q['txt'][:60]}")


def add_section(driver, title):
    js_click(driver, wait_for(
        lambda: next(iter(driver.find_elements(By.XPATH, "//*[@role='button' and @aria-label='Add section']")), None),
        "botón agregar sección",
    ))
    time.sleep(0.8)
    tb = wait_for(
        lambda: last_textbox(driver, "Section title (optional)"),
        "título de sección nueva",
    )
    fill_textbox(driver, tb, title)
    log(f"  ✓ Sección: {title}")


def main():
    opts = Options()
    opts.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=opts, service=Service(CHROMEDRIVER))

    try:
        log("Conectando a la ventana de Opera GX…")
        driver.get(CREATE_URL)
        wait_ready(driver)
        time.sleep(3)

        title = wait_for(lambda: last_textbox(driver, "Form title"), "editor del formulario", timeout=25)
        if title is None:
            log("⛔ El editor no cargó. Si ves una página de inicio de sesión de Google,")
            log("   inicia sesión con el correo del colegio en la ventana de Opera.")
            log("   El script reintenta automáticamente (hasta 10 min).")
            deadline = time.time() + LOGIN_TIMEOUT
            while time.time() < deadline:
                time.sleep(5)
                title = last_textbox(driver, "Form title")
                if title is not None:
                    log("✅ Sesión detectada. Continuando…")
                    break
                try:
                    driver.get(CREATE_URL)
                except Exception:
                    pass
            if title is None:
                log("⛔ Se agotó el tiempo de espera.")
                sys.exit(1)

        fill_textbox(driver, title, FORM_TITLE)
        log("✓ Título del formulario establecido")

        first_q = wait_for(lambda: last_textbox(driver, "Question"), "pregunta inicial")
        card0 = wait_for(
            lambda: first_q.find_element(
                By.XPATH, "./ancestor::div[.//*[@role='checkbox' and @aria-label='Required']][1]"
            ),
            "tarjeta de la pregunta inicial",
        )
        js_click(driver, wait_for(
            lambda: next(iter(card0.find_elements(By.XPATH, ".//*[@role='button' and @aria-label='Delete question']")), None),
            "botón eliminar",
        ))
        log("✓ Pregunta por defecto eliminada")

        for q in SECTIONS[0][1]:
            try:
                add_question(driver, q)
            except Exception as e:
                log(f"  ⚠ Error en pregunta '{q['txt'][:40]}': {e}")
        for sec_title, questions in SECTIONS[1:]:
            try:
                add_section(driver, sec_title)
            except Exception as e:
                log(f"  ⚠ Error en sección '{sec_title}': {e}")
            for q in questions:
                try:
                    add_question(driver, q)
                except Exception as e:
                    log(f"  ⚠ Error en pregunta '{q['txt'][:40]}': {e}")

        m = re.search(r"/d/([-\w]+)/edit", driver.current_url) or re.search(r"/d/([-\w]+)/", driver.current_url)
        form_id = m.group(1) if m else None

        link_el = wait_for(
            lambda: next(
                iter(driver.find_elements(By.XPATH, "//input[@aria-label and contains(@aria-label,'Link for sharing')]")),
                None,
            ),
            "enlace de respuesta",
            10,
        )
        public_url = link_el.get_attribute("value") or ""
        public_url = re.sub(r"\?usp=.*$", "", public_url)
        if not public_url and form_id:
            public_url = f"https://docs.google.com/forms/d/{form_id}/viewform"

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            f.write(public_url)

        log("=" * 62)
        log("✅ FORMULARIO CREADO CON ÉXITO")
        log(f"URL pública: {public_url}")
        log(f"(guardada también en {OUT_FILE})")
        log("=" * 62)
        log("Abriendo el enlace público en el navegador para verificación…")
        driver.get(public_url)
    except Exception as e:
        log(f"⛔ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
