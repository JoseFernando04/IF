"""Graba un clip vertical del tablero de publicaciones REAL (docs/panel/publicaciones.html) usado en compu y celular.

Para el formato `realidad` cuando no hay grabación del equipo: el tablero se abre con las piezas reales
(exportadas con `tools/publicaciones.py exportar-panel`), sin escribir nada en la base de datos (base simulada en memoria).
El cursor y el dedo siguen un guion de tiempos (segundos del reel) para caer sobre lo que dice la voz.

Uso:
  .venv/Scripts/python tools/grabar_tablero.py <carpeta-export> <salida.mp4> [--dur 22] [--muestra 2,10,15]
    --compu-hasta 13.1   cambio de la compu al celular
    --filtros 10.4,11.4,12.3   clics en Pendientes / Subidas / Descartadas
    --toque 14.6         el dedo marca «Subido» en la primera pieza
Oculta el párrafo de introducción y el pie del tablero (mencionan herramientas internas).
"""
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from ifcontent.core.config import ASSETS_DIR, ROOT, load_config
from ifcontent.video.ffmpeg import ffmpeg_bin

FPS = 30


def arg(nombre: str, defecto: str) -> str:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else defecto


def panel_html(piezas: list[dict], tema: str) -> str:
    html = (ROOT / "docs" / "panel" / "publicaciones.html").read_text(encoding="utf-8")
    f = ASSETS_DIR.joinpath("fonts").as_uri()
    fuentes = (f'<style>@font-face{{font-family:"Space Grotesk";src:url("{f}/SpaceGrotesk.ttf");font-weight:300 700}}'
               f'@font-face{{font-family:"Inter";src:url("{f}/Inter.ttf");font-weight:100 900}}'
               f'@font-face{{font-family:"JetBrains Mono";src:url("{f}/JetBrainsMono.ttf");font-weight:100 800}}'
               '.lede,footer{display:none!important}html{scrollbar-width:none}::-webkit-scrollbar{display:none}</style>')
    html = html.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', "")
    html = "\n".join(l for l in html.splitlines() if "fonts.googleapis.com/css2" not in l)
    stub = ("<script>(function(){const P=" + json.dumps(piezas, ensure_ascii=False) + ";"
            "const db={collection:()=>({onSnapshot(cb){setTimeout(()=>cb({metadata:{fromCache:false},"
            "docs:P.map(p=>({id:p.id,exists:true,data:()=>Object.assign({},p)}))}),0);return()=>{}},"
            "doc:()=>({update:async()=>{}})})};"
            "window.claude={use:async()=>db};"
            f"document.documentElement.dataset.theme='{tema}';}})();</script>")
    return stub + fuentes + html


ESCENA = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0a1410}
#grano{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 40%,#1d362b 0%,#0a1410 70%)}
.cont{position:absolute;transform-origin:50% 50%}
#compu{left:52px;top:250px;width:880px;height:1556px;transform-origin:0 0}
#compu .barra{height:56px;background:#e9e6da;border-radius:18px 18px 0 0;display:flex;align-items:center;gap:12px;padding:0 22px}
#compu .barra i{width:16px;height:16px;border-radius:50%;background:#c9c4b3}
#compu .barra b{margin-left:24px;height:30px;flex:1;max-width:520px;border-radius:15px;background:#fbf9f1}
#compu iframe{display:block;width:880px;height:1500px;border:0;background:#fefcf3;border-radius:0 0 18px 18px}
#cel{left:50%;top:50%;width:390px;height:844px;margin:-422px 0 0 -195px;padding:12px;border-radius:58px;background:#050806;
  box-shadow:0 0 0 3px #2a3a31,0 40px 120px rgba(0,0,0,.7)}
#cel iframe{width:390px;height:844px;border:0;border-radius:46px;background:#0a1410}
#cel .isla{position:absolute;left:50%;top:22px;width:110px;height:30px;margin-left:-55px;border-radius:16px;background:#000;z-index:3}
#cursor{position:absolute;width:30px;height:44px;z-index:9;pointer-events:none}
#dedo{position:absolute;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;background:rgba(254,252,243,.55);
  border:3px solid rgba(255,255,255,.85);z-index:9;pointer-events:none}
#onda{position:absolute;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;border:4px solid #f0c419;z-index:8;pointer-events:none}
#vineta{position:absolute;inset:0;background:radial-gradient(90% 70% at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.4) 100%);pointer-events:none;z-index:20}
</style></head><body>
<div id="grano"></div>
<div class="cont" id="compu"><div class="barra"><i></i><i></i><i></i><b></b></div><iframe id="fc"></iframe>
  <svg id="cursor" viewBox="0 0 30 44"><path d="M2 2 L2 36 L11 28 L17 42 L23 39 L17 26 L28 26 Z" fill="#fff" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/></svg></div>
<div class="cont" id="cel"><div class="isla"></div><iframe id="fm"></iframe><div id="onda"></div><div id="dedo"></div></div>
<div id="vineta"></div>
<script>
const G = __GUION__;
const $ = (id) => document.getElementById(id);
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eio = (x) => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eo = (x) => 1 - Math.pow(1 - cl(x), 3);
const listo = (f) => new Promise((ok) => { f.onload = ok; });
window.__ready = false;
(async () => {
  const a = listo($("fc")), b = listo($("fm"));
  $("fc").srcdoc = G.compu; $("fm").srcdoc = G.cel;
  await a; await b;
  await new Promise((r) => setTimeout(r, 400));
  const dc = $("fc").contentDocument, dm = $("fm").contentDocument;
  await dc.fonts.ready; await dm.fonts.ready;
  dc.querySelector('.filter[data-f="todo"]').click();
  dm.querySelector('.filter[data-f="todo"]').click();
  const hecho = new Set();
  const rect = (doc, sel) => { const r = doc.querySelector(sel).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
  // Compu: cursor que pasea y hace clic en los filtros al ritmo de la voz
  const filtros = ["pendiente", "publicado", "descartado"];
  let cur = [880, 700];
  window.__seek = async (t) => {
    const enCompu = t < G.compu_hasta;
    // Transición: la compu se va hacia arriba y entra el celular desde abajo (0,45 s)
    const k = eo((t - G.compu_hasta) / 0.45);
    const zc = 1.1 + 0.03 * cl(t / G.compu_hasta);
    $("compu").style.transform = `translateY(${-k * 2300}px) scale(${zc}) rotate(${-0.6 + 0.4 * Math.sin(t * 0.5)}deg)`;
    const zm = 2.05 + 0.04 * cl((t - G.compu_hasta) / 9);
    $("cel").style.transform = `translateY(${(1 - k) * 1900 + 95}px) scale(${zm}) rotate(${1.2 - 0.5 * cl((t - G.compu_hasta) / 9)}deg)`;
    // Scroll de la compu: baja despacio mientras habla del problema; vuelve arriba para los filtros
    const winC = $("fc").contentWindow;
    const tf = G.filtros[0] - 0.9;
    winC.scrollTo(0, t < tf ? 520 * eio(t / tf) : 520 * (1 - eio((t - tf) / 0.6)));
    // Cursor
    let destino = [880, 760];
    G.filtros.forEach((tc, i) => {
      if (t >= tc - 0.55) destino = rect(dc, `.filter[data-f="${filtros[i]}"]`);
      if (t >= tc && !hecho.has("f" + i)) { hecho.add("f" + i); dc.querySelector(`.filter[data-f="${filtros[i]}"]`).click(); }
    });
    if (t >= G.compu_hasta - 0.5 && !hecho.has("todo")) { hecho.add("todo"); dc.querySelector('.filter[data-f="todo"]').click(); }
    cur = [cur[0] + (destino[0] - cur[0]) * 0.22, cur[1] + (destino[1] - cur[1]) * 0.22];
    const yS = 56;  // alto de la barra del navegador
    $("cursor").style.left = (cur[0] - 4) + "px"; $("cursor").style.top = (cur[1] + yS - 2) + "px";
    $("cursor").style.opacity = enCompu ? 1 : 0;
    // Celular: el dedo baja a «Subido» de la primera pieza y lo toca
    const winM = $("fm").contentWindow;
    const tt = G.toque;
    const sel = '#days .row .seg button[data-v="publicado"]';
    const yScroll = t < tt + 1.4 ? 0 : 900 * eio((t - tt - 1.4) / 5.5);
    winM.scrollTo(0, yScroll);
    const [bx, by] = rect(dm, sel);
    const p = eo((t - (tt - 0.9)) / 0.8);
    const fx = 330 + (bx - 330) * p, fy = 760 + (by - 760) * p;
    const sale = eo((t - tt - 0.35) / 0.5);
    $("dedo").style.left = (fx + 12 + sale * 120) + "px"; $("dedo").style.top = (fy + 12 + sale * 260) + "px";
    $("dedo").style.opacity = t > tt - 1.0 && t < tt + 1.0 ? (t < tt ? 1 : 1 - sale) : 0;
    $("dedo").style.transform = `scale(${t >= tt && t < tt + 0.18 ? 0.82 : 1})`;
    const o = cl((t - tt) / 0.5);
    $("onda").style.left = (bx + 12) + "px"; $("onda").style.top = (by + 12) + "px";
    $("onda").style.opacity = t >= tt ? 1 - o : 0; $("onda").style.transform = `scale(${1 + o * 1.6})`;
    if (t >= tt && !hecho.has("toque")) { hecho.add("toque"); dm.querySelector(sel).click(); }
    await new Promise((r) => requestAnimationFrame(() => r()));
  };
  window.__ready = true;
})();
</script></body></html>"""


def main() -> None:
    load_config()
    carpeta, destino = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    piezas = [json.loads(p.read_text(encoding="utf-8")) | {"id": p.stem} for p in sorted(carpeta.glob("*.json"))]
    guion = {"compu": panel_html(piezas, "light"), "cel": panel_html(piezas, "dark"),
             "compu_hasta": float(arg("--compu-hasta", "13.1")),
             "filtros": [float(x) for x in arg("--filtros", "10.4,11.4,12.3").split(",")],
             "toque": float(arg("--toque", "14.6"))}
    dur = float(arg("--dur", "22"))
    muestra = arg("--muestra", "")
    work = destino.parent / "work-grabacion"
    work.mkdir(parents=True, exist_ok=True)
    for viejo in work.glob("*"):
        viejo.unlink()
    escena = work / "escena.html"
    escena.write_text(ESCENA.replace("__GUION__", json.dumps(guion, ensure_ascii=False).replace("</", "<\/")), encoding="utf-8")
    tiempos = [float(x) for x in muestra.split(",")] if muestra else [i / FPS for i in range(int(dur * FPS))]
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files"])
        page = b.new_page(viewport={"width": 1080, "height": 1920})
        page.on("pageerror", lambda e: print("  [error JS]", e))
        page.goto(escena.as_uri())
        page.wait_for_function("window.__ready === true", timeout=30000)
        # Los clics dependen del orden: se recorre siempre desde 0 (las muestras pasan por los tiempos intermedios).
        todos = sorted(set(tiempos) | ({i / FPS for i in range(int(max(tiempos) * FPS))} if muestra else set()))
        for i, t in enumerate(todos):
            page.evaluate("t => window.__seek(t)", t)
            if t in tiempos:
                page.screenshot(path=str(work / f"{len([x for x in todos[:i] if x in tiempos]) + 1:04d}.jpg"), type="jpeg", quality=92)
            if i % 150 == 0:
                print(f"  cuadro {i}/{len(todos)}")
        b.close()
    if muestra:
        print("✔ muestras en", work)
        return
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(work / "%04d.jpg"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", str(destino)], check=True)
    print("✔", destino, f"({dur:.1f} s)")


if __name__ == "__main__":
    main()
