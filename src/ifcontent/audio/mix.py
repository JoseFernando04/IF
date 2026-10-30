"""Mezcla final: voz + música con ducking (la música baja cuando habla la voz) y normalización."""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..core.config import load_config
from ..video.ffmpeg import ffmpeg_bin


def mix_audio(voice_wav: Path | None, music: Path, duration: float, out: Path) -> Path:
    s = load_config().settings["music"]
    fade_out = min(2.0, duration / 4)
    music_chain = (
        f"[{1 if voice_wav else 0}:a]aresample=48000,atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        f"volume={s['volume_db'] if voice_wav else s['volume_no_voice_db']}dB,"
        f"afade=t=in:d=0.6,afade=t=out:st={duration - fade_out:.3f}:d={fade_out:.3f}"
    )
    cmd = [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error"]
    if voice_wav:
        cmd += ["-i", str(voice_wav)]
    cmd += ["-stream_loop", "-1", "-i", str(music)]
    if voice_wav:
        graph = (
            f"{music_chain}[m];"
            "[0:a]aresample=48000,asplit=2[v][sc];"
            "[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[md];"
            "[v][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
        )
    else:
        graph = f"{music_chain},loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    cmd += ["-filter_complex", graph, "-map", "[a]", "-t", f"{duration:.3f}", "-ar", "48000", "-ac", "2", str(out)]
    subprocess.run(cmd, check=True)
    return out


def build_sfx_track(events: list[dict], duration: float, out: Path, voice: Path | None = None) -> Path:
    """Arma una pista con los efectos de sonido (assets/sfx) en sus tiempos exactos, y opcionalmente la voz.

    events: [{"t": 0.8, "sfx": "thud", "gain_db": -3}, ...]
    """
    import numpy as np
    import soundfile as sf

    from ..core.config import ASSETS_DIR

    sr = 48000
    track = np.zeros(int((duration + 1) * sr), dtype=np.float32)
    if voice:
        v, vsr = sf.read(voice, dtype="float32")
        if vsr != sr:
            v = np.interp(np.linspace(0, len(v) - 1, int(len(v) * sr / vsr)), np.arange(len(v)), v).astype(np.float32)
        track[: min(len(v), len(track))] += v[: len(track)]
    for e in events:
        clip, csr = sf.read(ASSETS_DIR / "sfx" / f"{e['sfx']}.wav", dtype="float32")
        assert csr == sr, "los SFX deben estar a 48 kHz (tools/make_sfx.py)"
        i0 = int(e["t"] * sr)
        seg = clip[: max(0, len(track) - i0)] * 10 ** (e.get("gain_db", 0) / 20)
        track[i0 : i0 + len(seg)] += seg
    sf.write(out, track[: int(duration * sr)], sr)
    return out
