# -*- coding: utf-8 -*-
"""Pagina de ventas: SEO (descripcion, canonica, redes, datos estructurados), robots.txt, sitemap.xml
y Google Analytics 4 con aviso de cookies (solo carga Analytics si la persona acepta).
Uso (desde la carpeta donde esta index.html):  python aplicar_ventas_seo.py G-XXXXXXXXXX [--check]
Idempotente, con copia .bak, aborta sin tocar nada si algo no coincide."""
import sys, os, re, shutil, time, datetime

args = [a for a in sys.argv[1:] if not a.startswith("--")]
CHECK = "--check" in sys.argv
if len(args) != 1 or not re.fullmatch(r"G-[A-Z0-9]{6,14}", args[0]):
    sys.exit("Uso: python aplicar_ventas_seo.py G-XXXXXXXXXX   (el ID de medicion de Google Analytics 4, empieza con G-)")
GA = args[0]
SITE = "https://ventas.biopathsentinel.org/"
PRIV = "https://demo.biopathsentinel.org/privacidad"
BASE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(BASE, "index.html")
if not os.path.exists(F):
    sys.exit("No encuentro index.html en esta carpeta. Guarda este script junto a index.html.")

raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf")
t0 = raw.decode("utf-8-sig"); crlf = "\r\n" in t0; t = t0.replace("\r\n", "\n")

if "G-" in t and "gtag(" in t:
    print("index.html: Google Analytics ya esta instalado, no se toca."); done_html = True
else:
    done_html = False

TITLE_OLD = "<title>BioPath HCE Enterprise</title>"
DESC = "HiSalud: historia clínica electrónica para consultorios y clínicas de Colombia. Agenda, odontología, hospitalización, facturación con copago, RIPS y RDA en un solo lugar. Pide tu demostración gratis."
HEAD = f'''<title>BioPath HCE Enterprise · Historia clínica electrónica para IPS en Colombia</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0b7a84">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="BioPath HCE Enterprise">
<meta property="og:title" content="BioPath HCE Enterprise · Historia clínica electrónica para IPS en Colombia">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="BioPath HCE Enterprise · Historia clínica electrónica para IPS en Colombia">
<meta name="twitter:description" content="{DESC}">
<script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"Organization","name":"BioPath-Sentinel AI","url":"{SITE}","areaServed":"CO"}},{{"@type":"SoftwareApplication","name":"BioPath HCE Enterprise (HiSalud)","applicationCategory":"HealthApplication","operatingSystem":"Web","inLanguage":"es-CO","description":"{DESC}","offers":{{"@type":"AggregateOffer","priceCurrency":"COP","lowPrice":"300000","highPrice":"1800000","offerCount":"4"}}}}]}}</script>'''

BANNER = f'''
<style>
#ck{{position:fixed;left:12px;right:12px;bottom:12px;z-index:50;max-width:640px;margin:0 auto;background:var(--card,#fff);color:var(--ink,#0c2430);border:1px solid var(--line,#cfdcdc);border-radius:12px;padding:16px 18px;box-shadow:0 10px 30px rgba(0,0,0,.2);font-size:.92rem;display:none}}
#ck p{{margin:0 0 12px}}#ck a{{color:var(--accent,#0b7a84)}}
#ck .r{{display:flex;gap:10px;flex-wrap:wrap}}
#ck button{{font:inherit;font-weight:600;padding:9px 18px;border-radius:9px;border:2px solid var(--accent,#0b7a84);cursor:pointer;background:var(--accent,#0b7a84);color:var(--accent-ink,#fff)}}
#ck button.o{{background:transparent;color:inherit}}
</style>
<div id="ck" role="dialog" aria-label="Preferencias de cookies"><p>Usamos cookies de analítica (Google Analytics) para saber cuántas personas visitan esta página y mejorarla. Solo se activan si aceptas. Más información en nuestra <a href="{PRIV}" target="_blank" rel="noopener">política de tratamiento de datos</a>.</p><div class="r"><button type="button" id="ckSi">Aceptar</button><button type="button" id="ckNo" class="o">Rechazar</button></div></div>
<script>
(function(){{
  var ID="{GA}",K="bp_cookies",b=document.getElementById("ck");
  function get(){{try{{return localStorage.getItem(K)}}catch(e){{return null}}}}
  function set(v){{try{{localStorage.setItem(K,v)}}catch(e){{}}}}
  function cargar(){{
    if(window.gtag)return;
    var s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+ID;document.head.appendChild(s);
    window.dataLayer=window.dataLayer||[];window.gtag=function(){{dataLayer.push(arguments)}};
    gtag("js",new Date());gtag("config",ID,{{anonymize_ip:true}});
  }}
  var v=get();
  if(v==="si")cargar();else if(v!=="no")b.style.display="block";
  document.getElementById("ckSi").onclick=function(){{set("si");b.style.display="none";cargar()}};
  document.getElementById("ckNo").onclick=function(){{set("no");b.style.display="none"}};
}})();
</script>'''

if not done_html:
    if t.count(TITLE_OLD) != 1:
        sys.exit(f"ABORTO: <title> original aparece {t.count(TITLE_OLD)} veces (esperaba 1; ¿ya se cambió el título?). No se cambió nada.")
    if t.count("</footer>") != 1:
        sys.exit(f"ABORTO: </footer> aparece {t.count('</footer>')} veces (esperaba 1). No se cambió nada.")
    if "canonical" in t or 'name="description"' in t:
        sys.exit("ABORTO: la página ya tiene descripción o canonical; revísalo a mano. No se cambió nada.")
    t = t.replace(TITLE_OLD, HEAD).replace("</footer>", "</footer>" + BANNER)

hoy = datetime.date.today().isoformat()
ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"
SITEMAP = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{SITE}</loc><lastmod>{hoy}</lastmod><changefreq>monthly</changefreq><priority>1.0</priority></url>\n</urlset>\n'

if CHECK:
    print("Modo --check: no se escribió nada. Todo coincide."); sys.exit(0)
if not done_html:
    shutil.copy2(F, F + ".bak_" + time.strftime("%Y%m%d%H%M%S"))
    out = t.replace("\n", "\r\n") if crlf else t
    open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    print("index.html actualizado.")
for nombre, cont in (("robots.txt", ROBOTS), ("sitemap.xml", SITEMAP)):
    p = os.path.join(BASE, nombre)
    if os.path.exists(p): print(nombre + ": ya existe, no se toca.")
    else: open(p, "w", encoding="utf-8", newline="\n").write(cont); print(nombre + ": creado.")
print("Listo.")
