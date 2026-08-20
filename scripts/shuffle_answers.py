import sys, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from bs4 import BeautifulSoup
except ImportError as e:
    print("FALTA bs4:", e); sys.exit(1)

path = r"C:\Users\RoSH\Documents\Once\taller_grado_once.html"
soup = BeautifulSoup(open(path, encoding="utf-8"), "html.parser")

letras = ["A", "B", "C"]
random.seed(42)
total = 0
for preg in soup.select("div.pregunta"):
    opciones = preg.select_one("div.opciones")
    if not opciones:
        continue
    opts = opciones.find_all("div", class_="opcion", recursive=False)
    if len(opts) != 3:
        continue
    # cual es la correcta
    idx_correcta = next((i for i, o in enumerate(opts) if "correcta" in o.get("class", [])), None)
    if idx_correcta is None:
        continue
    orden = list(range(3))
    random.shuffle(orden)
    nueva_correcta = orden.index(idx_correcta)  # posicion nueva del correcto
    # reasignar clases y letras
    new_opts = []
    for nueva_pos, orig_i in enumerate(orden):
        o = opts[orig_i]
        cls = o.get("class", [])
        cls = [c for c in cls if c != "correcta"]
        if nueva_pos == nueva_correcta:
            cls.append("correcta")
        o["class"] = cls
        letra = o.select_one("span.letra")
        if letra:
            letra.string = f"{letras[nueva_pos]})"
        new_opts.append(o)
    # reemplazar contenido de opciones y actualizar data-resp
    opciones.clear()
    for o in new_opts:
        opciones.append(o)
    preg["data-resp"] = letras[nueva_correcta].lower()
    total += 1

open(path, "w", encoding="utf-8").write(str(soup))
print("Preguntas barajadas:", total)