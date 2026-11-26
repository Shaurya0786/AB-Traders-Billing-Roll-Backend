import asyncio
import html as html_lib
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("uvicorn")

PCS_PER_BOX = 50  # every product is sold in boxes of 50 pieces


class NotificationService:
    def __init__(self):
        self.gmail_sender = os.getenv("GMAIL_SENDER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.notify_email = os.getenv("NOTIFY_EMAIL")

    async def send_email(self, inquiry) -> None:
        """Send a Gmail notification for a new inquiry."""
        if not all([self.gmail_sender, self.gmail_password, self.notify_email]):
            logger.warning("Gmail env vars not set — skipping email notification.")
            return

        try:
            await asyncio.to_thread(self._send_email_sync, inquiry)
            logger.info(f"Inquiry notification email sent for {inquiry.get('full_name')}")
        except Exception as e:
            logger.error(f"Failed to send inquiry notification email: {e}")

    def _send_email_sync(self, inquiry) -> None:
        subject, html = render_inquiry_email(inquiry)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.gmail_sender
        msg["To"] = self.notify_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.gmail_sender, self.gmail_password)
            server.sendmail(self.gmail_sender, self.notify_email, msg.as_string())


def render_inquiry_email(inquiry) -> tuple[str, str]:
    """The subject and HTML body of the new-enquiry email. Everything the visitor typed is escaped, so a
    message cannot put its own links or markup into the email."""
    def e(key):
        value = inquiry.get(key)
        return html_lib.escape(str(value)) if value not in (None, "") else "—"

    is_custom = inquiry.get("is_custom_quote", False)
    inquiry_type = "Custom Quote Request" if is_custom else "General Inquiry"
    name = str(inquiry.get("full_name") or "Unknown").replace("\r", " ").replace("\n", " ")
    subject = f"New inquiry from {name}"
    if not subject.isascii():
        subject = "New inquiry from the website"

    def row(label, key):
        return (f'<tr><td style="padding:8px; border:1px solid #ddd;"><strong>{label}</strong></td>'
                f'<td style="padding:8px; border:1px solid #ddd; white-space:pre-wrap;">{e(key)}</td></tr>')

    rows = []
    items = inquiry.get("items") or []
    if items:
        lines = "<br>".join(f"{html_lib.escape(str(it.get('product_name') or it.get('product_slug')))}: "
                            f"{int(it.get('boxes') or 0)} boxes ({int(it.get('boxes') or 0) * PCS_PER_BOX} pcs)" for it in items)
        rows.append('<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Products</strong></td>'
                    f'<td style="padding:8px; border:1px solid #ddd;">{lines}</td></tr>')
    rows += [row("Name", "full_name"), row("Email", "email"), row("Phone", "phone_number"), row("Company", "company_name"),
            row("Product Type", "product_type"), row("Estimated Qty", "estimated_quantity"), row("Message", "message")]
    if is_custom:
        rows += [row("Roll Width", "roll_width"), row("Roll Diameter", "roll_diameter"), row("Exact Quantity", "exact_quantity")]
    html = f"""
        <html><body style="font-family: Arial, sans-serif; color: #333;">
          <h2 style="color: #1a73e8;">New {inquiry_type} Received</h2>
          <table style="border-collapse: collapse; width: 100%;">{''.join(rows)}</table>
          <p style="color:#888; font-size:12px; margin-top:20px;">AB Traders — Auto Notification</p>
        </body></html>
        """
    return subject, html
