"""Publicador de simulación: escribe exactamente qué llamadas haría a Instagram y TikTok, sin hacerlas."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

TUNNEL = "https://<túnel-temporal>.trycloudflare.com"


class DryRunPublisher:
    def publish(self, piece: dict) -> dict:
        out = Path(piece["output_dir"])
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        caption = (out / "caption.txt").read_text(encoding="utf-8")
        if piece["kind"] == "reel":
            ig = [
                {"POST": "graph.instagram.com/<IG_USER_ID>/media",
                 "data": {"media_type": "REELS", "video_url": f"{TUNNEL}/reel.mp4", "cover_url": f"{TUNNEL}/cover.jpg",
                          "caption": caption, "share_to_feed": True}},
                {"GET": "graph.instagram.com/<CONTAINER_ID>?fields=status_code", "until": "FINISHED"},
                {"POST": "graph.instagram.com/<IG_USER_ID>/media_publish", "data": {"creation_id": "<CONTAINER_ID>"}},
            ]
            tiktok = [
                {"POST": "open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                 "data": {"source_info": {"source": "FILE_UPLOAD", "video_size": Path(manifest["media"]["video"]).stat().st_size}}},
                {"PUT": "<upload_url>", "file": "reel.mp4"},
                {"note": "El video queda como borrador en la bandeja de TikTok; se publica a mano desde la app."},
            ]
        else:
            images = manifest["media"]["images"]
            ig = [
                *({"POST": "graph.instagram.com/<IG_USER_ID>/media",
                   "data": {"image_url": f"{TUNNEL}/{Path(p).name}", "is_carousel_item": True}} for p in images),
                {"POST": "graph.instagram.com/<IG_USER_ID>/media",
                 "data": {"media_type": "CAROUSEL", "children": [f"<CHILD_{i}>" for i in range(1, len(images) + 1)], "caption": caption}},
                {"POST": "graph.instagram.com/<IG_USER_ID>/media_publish", "data": {"creation_id": "<CAROUSEL_ID>"}},
            ]
            tiktok = [{"note": "Carrusel de fotos: se envía por correo para subirlo a mano (TikTok exige dominio verificado)."}]
        result = {"simulated_at": datetime.now().isoformat(timespec="seconds"), "dry_run": True,
                  "instagram": ig, "tiktok": tiktok}
        (out / "publish_simulation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result
