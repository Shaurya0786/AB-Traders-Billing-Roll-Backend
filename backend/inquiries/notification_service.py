import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("uvicorn")


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
        subject = f"📋 New Inquiry — {inquiry.get('full_name', 'Unknown')}"

        # Build plain-text + HTML body
        is_custom = inquiry.get("is_custom_quote", False)
        inquiry_type = "Custom Quote Request" if is_custom else "General Inquiry"

        html = f"""
        <html><body style="font-family: Arial, sans-serif; color: #333;">
          <h2 style="color: #1a73e8;">New {inquiry_type} Received</h2>
          <table style="border-collapse: collapse; width: 100%;">
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Name</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('full_name', '—')}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Email</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('email', '—')}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Phone</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('phone_number', '—')}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Company</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('company_name') or '—'}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Product Type</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('product_type') or '—'}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Estimated Qty</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('estimated_quantity') or '—'}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Message</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('message') or '—'}</td></tr>
            {"" if not is_custom else f'''
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Roll Width</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('roll_width') or '—'}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Roll Diameter</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('roll_diameter') or '—'}</td></tr>
            <tr><td style="padding:8px; border:1px solid #ddd;"><strong>Exact Quantity</strong></td>
                <td style="padding:8px; border:1px solid #ddd;">{inquiry.get('exact_quantity') or '—'}</td></tr>
            '''}
          </table>
          <p style="color:#888; font-size:12px; margin-top:20px;">AB Traders — Auto Notification</p>
        </body></html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.gmail_sender
        msg["To"] = self.notify_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.gmail_sender, self.gmail_password)
            server.sendmail(self.gmail_sender, self.notify_email, msg.as_string())
