"""Avisos: correo SMTP si está configurado en .env; si no, quedan en data/notifications.log."""
from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from .config import load_config

log = logging.getLogger(__name__)


def notify(subject: str, body: str) -> None:
    cfg = load_config()
    log_path = cfg.path("output").parent / "notifications.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {subject}\n{body}\n\n")

    host, user, password = os.getenv("SMTP_HOST"), os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
    to = os.getenv("NOTIFY_TO") or cfg.brand["email"]
    if not (host and user and password):
        log.info("Aviso registrado (SMTP sin configurar): %s", subject)
        return
    msg = EmailMessage()
    msg["Subject"] = f"[IF Contenido] {subject}"
    msg["From"] = user
    msg["To"] = to
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=30) as s:
            s.starttls()
            s.login(user, password)
            s.send_message(msg)
        log.info("Aviso enviado por correo: %s", subject)
    except Exception as e:  # el aviso nunca debe tumbar el pipeline
        log.error("No se pudo enviar el correo de aviso: %s", e)
