import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger("uvicorn")

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

_INTERNAL_HTML = _env.get_template("internal_inquiry.html")
_INTERNAL_TXT = _env.get_template("internal_inquiry.txt")
_CLIENT_HTML = _env.get_template("client_ack.html")
_CLIENT_TXT = _env.get_template("client_ack.txt")


def _sanitize_header(value: str) -> str:
    """Strip CR/LF so a crafted name can't inject extra headers (e.g. Bcc)."""
    if not value:
        return ""
    return str(value).replace("\r", "").replace("\n", "").strip()


class NotificationService:
    def __init__(self):
        self.gmail_sender = os.getenv("GMAIL_SENDER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.notify_email = os.getenv("NOTIFY_EMAIL")

    async def send_notifications(self, inquiry) -> None:
        """Fire both the internal notification and the client acknowledgement."""
        if not self.gmail_sender or not self.gmail_password:
            logger.warning("Gmail env vars not set — skipping all email notifications.")
            return

        results = await asyncio.gather(
            self._send_internal(inquiry),
            self._send_client_ack(inquiry),
            return_exceptions=True,
        )
        for label, result in zip(("internal", "client-ack"), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to send {label} email: {result}")

    async def _send_internal(self, inquiry) -> None:
        if not self.notify_email:
            logger.warning("NOTIFY_EMAIL not set — skipping internal notification.")
            return

        full_name = _sanitize_header(inquiry.get("full_name") or "Unknown")
        subject = f"📋 New Inquiry — {full_name}"
        html = _INTERNAL_HTML.render(**inquiry)
        text = _INTERNAL_TXT.render(**inquiry)

        await asyncio.to_thread(
            self._send_sync, self.notify_email, subject, text, html
        )
        logger.info(f"Internal inquiry email sent for {full_name}")

    async def _send_client_ack(self, inquiry) -> None:
        recipient = inquiry.get("email")
        if not recipient:
            logger.warning("Inquiry missing email — skipping client acknowledgement.")
            return

        subject = "We received your inquiry — AB Traders"
        html = _CLIENT_HTML.render(**inquiry)
        text = _CLIENT_TXT.render(**inquiry)

        await asyncio.to_thread(self._send_sync, recipient, subject, text, html)
        logger.info(f"Client acknowledgement email sent to {recipient}")

    def _send_sync(self, to_addr: str, subject: str, text_body: str, html_body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = _sanitize_header(subject)
        msg["From"] = self.gmail_sender
        msg["To"] = to_addr
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.gmail_sender, self.gmail_password)
            server.sendmail(self.gmail_sender, [to_addr], msg.as_string())
