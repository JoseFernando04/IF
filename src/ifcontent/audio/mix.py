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
