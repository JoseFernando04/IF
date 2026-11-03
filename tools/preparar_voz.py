"""Prepara las grabaciones de voz reales de assets/voice/<persona>/ (ver docs/guia-grabar-voces.md).

Uso: .venv/Scripts/python tools/preparar_voz.py
Por cada persona CON permiso (cualquier archivo con "permiso" en el nombre):
- Transcribe cada audio (Whisper local) y detecta si es la REFERENCIA (para clonar) o el GUION del reel.
- Referencia → referencia.limpio.wav (máx. 30 s).
- Guion en un solo archivo → lo corta en frase1..5.limpio.wav con los tiempos de cada palabra.
- Archivos ya nombrados referencia.* / fraseN.* se usan tal cual.
Limpieza: filtro de graves, reducción de ruido suave, sin silencios al inicio/final, volumen nivelado, mono 48 kHz.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from probar_voces import GUION, TEXTO_REFERENCIA  # noqa: E402

from ifcontent.audio.enhance import mejorar  # noqa: E402
from ifcontent.audio.transcribe import cortes_por_frase, parecido, transcribir  # noqa: E402
from ifcontent.core.config import ASSETS_DIR, load_config  # noqa: E402
from ifcontent.video.ffmpeg import ffmpeg_bin  # noqa: E402

VOCES = ASSETS_DIR / "voice"
EXT = {".m4a", ".mp3", ".ogg", ".opus", ".wav", ".aac", ".flac", ".webm", ".mp4"}
TEXTO_GUIA = ("Hola, ¿cómo estás? Te cuento rápido cómo trabajamos. Primero platicamos de tu negocio: qué vendés, "
              "cómo llevás el inventario y qué es lo que más te quita tiempo. Después te mostramos, con ejemplos de "
              "verdad, cómo se vería todo ordenado. Sin tecnicismos y sin compromiso. ¿Te parece si lo vemos esta semana?")
LIMPIEZA = "highpass=f=80,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=7"
GENERADOS: list[Path] = []  # archivos .limpio.wav de esta corrida; al final pasan por la limpieza con IA
SIN_SILENCIOS = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,"
                 "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse,")


def exportar(origen: Path, destino: Path, desde: float | None = None, hasta: float | None = None,
             recortar_silencio: bool = True, max_s: float | None = None) -> float:
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error"]
    if desde is not None:
        cmd += ["-ss", f"{desde:.3f}", "-to", f"{hasta:.3f}"]
    cmd += ["-i", str(origen), "-af", (SIN_SILENCIOS if recortar_silencio else "") + LIMPIEZA, "-ac", "1", "-ar", "48000"]
    if max_s:
        cmd += ["-t", str(max_s)]
    subprocess.run(cmd + [str(destino)], check=True)
    GENERADOS.append(destino)
    return sf.info(destino).duration


def mejor_tramo(wav: Path, dur_s: float = 11.0) -> float:
    """Chatterbox usa ~10 s de la referencia: deja en el archivo el tramo con más voz y menos huecos."""
    import numpy as np

    x, sr = sf.read(wav, dtype="float32")
    if len(x) <= dur_s * sr:
        return len(x) / sr
    w = int(0.02 * sr)
    n = len(x) // w
    db = 20 * np.log10(np.sqrt((x[: n * w].reshape(n, w) ** 2).mean(1) + 1e-12))
    activo = db > (np.percentile(db, 90) - 25)
    largo, mejor, mejor_i = int(dur_s / 0.02), -1.0, 0
    for i in range(0, n - largo, 25):  # cada 0,5 s
        if not activo[i] and activo[i + 1]:  # empezar justo en el arranque de una palabra
            score = activo[i:i + largo].mean()
            if score > mejor:
                mejor, mejor_i = score, i
    sf.write(wav, x[mejor_i * w: mejor_i * w + int(dur_s * sr)], sr)
    return dur_s


def dialogos_de(persona: str) -> list[tuple[str, list[int], list[str]]]:
    """Líneas que le tocan a esta persona en cada guion de conversación (prototypes/**/guion.yaml)."""
    import yaml

    from ifcontent.core.config import ROOT

    salida = []
    for g_path in sorted((ROOT / "prototypes").glob("**/guion.yaml")):
        g = yaml.safe_load(g_path.read_text(encoding="utf-8"))
        claves = [k for k, p in g.get("personajes", {}).items() if p.get("voz") == persona]
        idx = [i for i, l in enumerate(g.get("lineas", [])) if l["quien"] in claves]
        if idx:
            salida.append((g["titulo"], idx, [g["lineas"][i]["texto"] for i in idx]))
    return salida


def preparar() -> None:
    load_config()
    personas = [p for p in sorted(VOCES.iterdir()) if p.is_dir()] if VOCES.exists() else []
    if not personas:
        print(f"No hay carpetas de personas en {VOCES}")
        return
    for persona in personas:
        if not any("permiso" in f.name.lower() for f in persona.iterdir()):
            print(f"✗ {persona.name}: falta el permiso (un archivo con 'permiso' en el nombre). No se procesa.")
            continue
        audios = [f for f in sorted(persona.iterdir()) if f.suffix.lower() in EXT and ".limpio" not in f.name]
        if not audios:
            print(f"✗ {persona.name}: no hay grabaciones")
            continue
        textos = transcribir(audios)
        (persona / "transcripciones.json").write_text(json.dumps(textos, ensure_ascii=False, indent=1), encoding="utf-8")
        for f in audios:
            t = textos[str(f)]
            nombre = f.stem.lower()
            es_frase = re.fullmatch(r"frase\d+", nombre)
            p_ref = max(parecido(t["text"], TEXTO_GUIA), parecido(t["text"], TEXTO_REFERENCIA))
            p_guion = parecido(t["text"], " ".join(GUION))
            dialogo = max(((parecido(t["text"], " ".join(txt)), titulo, idx, txt)
                           for titulo, idx, txt in dialogos_de(persona.name)), default=(0, "", [], []))
            if dialogo[0] > max(p_guion, p_ref, 0.5):
                p_d, titulo, idx, txt = dialogo
                print(f"• {persona.name}: {f.name} son sus líneas de «{titulo}» (parecido {p_d:.0%}); cortando…")
                for i, (a, b) in zip(idx, cortes_por_frase(t, txt)):
                    dur = exportar(f, persona / f"linea{i + 1:02d}.limpio.wav", a, b, recortar_silencio=False)
                    print(f"  ✔ linea{i + 1:02d}.limpio.wav ({dur:.1f} s)")
            elif es_frase:
                dur = exportar(f, persona / f"{nombre}.limpio.wav")
                print(f"✔ {persona.name}/{nombre}.limpio.wav ({dur:.1f} s)")
            elif nombre == "referencia" or p_ref > max(p_guion, 0.5):
                dur = exportar(f, persona / "referencia.limpio.wav", max_s=30)
                print(f"✔ {persona.name}/referencia.limpio.wav ({dur:.1f} s) ← {f.name} (parecido {p_ref:.0%})")
                if dur < 12:
                    print(f"  ⚠ La referencia dura {dur:.1f} s: con menos de 12 s el clon puede cortar frases. Grabá 20-30 s.")
            elif p_guion > 0.5:
                print(f"• {persona.name}: {f.name} es el guion del reel (parecido {p_guion:.0%}); cortando en frases…")
                for i, (a, b) in enumerate(cortes_por_frase(t, GUION), start=1):
                    dur = exportar(f, persona / f"frase{i}.limpio.wav", a, b, recortar_silencio=False)
                    print(f"  ✔ frase{i}.limpio.wav ({dur:.1f} s): {GUION[i - 1]}")
            else:
                print(f"? {persona.name}: no reconozco {f.name}: «{t['text'][:80]}…»")
        if GENERADOS:
            print(f"  … limpieza con IA (eco + ruido) de {len(GENERADOS)} archivos de {persona.name}")
            mejorar([(g, g) for g in GENERADOS])
            for g in GENERADOS:
                if g.name == "referencia.limpio.wav":
                    mejor_tramo(g)
            GENERADOS.clear()


if __name__ == "__main__":
    preparar()
