import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import re

from emailer.utils.settings import get_mail_settings
from emailer.schemas import SendMailRequest
from emailer.paths import UPLOAD_DIR
from fastapi import HTTPException


def extract_local_images(html: str):
    return re.findall(r'<img[^>]+src=["\'](uploads/[^"\']+)["\']', html)


def generate_cid_for_image(image_path):
    filename = Path(image_path).name
    return f"img_{filename.split('.')[0]}"


def resolve_account(from_address: str | None):
    settings = get_mail_settings()
    if from_address:
        if settings.accounts and from_address in {acc.address for acc in settings.accounts.values()}:
            for acc in settings.accounts.values():
                if acc.address == from_address:
                    return acc
        if settings.schreiber and settings.schreiber.address == from_address:
            return settings.schreiber
        raise HTTPException(status_code=400, detail="Selected from address not configured")
    if settings.accounts:
        return list(settings.accounts.values())[0]
    if settings.schreiber:
        return settings.schreiber
    raise HTTPException(status_code=500, detail="No mail account configured")


def build_message(account, payload: SendMailRequest):
    local_images = extract_local_images(payload.html_body)
    if local_images:
        msg = MIMEMultipart('related')
        msg["Subject"] = payload.betreff
        msg["From"] = account.address
        msg["To"] = str(payload.recipient)
        msg["Bcc"] = account.address
        html_body = payload.html_body
        for image_url in local_images:
            image_path = UPLOAD_DIR / Path(image_url).name
            if image_path.exists():
                cid = generate_cid_for_image(image_url)
                html_body = html_body.replace(image_url, f"cid:{cid}")
        msg_alt = MIMEMultipart('alternative')
        msg.attach(msg_alt)
        msg_alt.attach(MIMEText("Please enable HTML to view this email.", 'plain'))
        msg_alt.attach(MIMEText(html_body, 'html'))
        for image_url in local_images:
            image_path = UPLOAD_DIR / Path(image_url).name
            if image_path.exists():
                cid = generate_cid_for_image(image_url)
                file_ext = image_path.suffix.lower()
                if file_ext == '.png':
                    subtype = 'png'
                elif file_ext in ['.jpg', '.jpeg']:
                    subtype = 'jpeg'
                elif file_ext == '.gif':
                    subtype = 'gif'
                else:
                    subtype = 'png'
                with open(image_path, "rb") as f:
                    img_data = f.read()
                img = MIMEImage(img_data, _subtype=subtype)
                img.add_header('Content-ID', f'<{cid}>')
                img.add_header('Content-Disposition', 'inline', filename=image_path.name)
                msg.attach(img)
        return msg
    else:
        msg = EmailMessage()
        msg["Subject"] = payload.betreff
        msg["From"] = account.address
        msg["To"] = str(payload.recipient)
        msg["Bcc"] = account.address
        msg.set_content("Please enable HTML to view this email.")
        msg.add_alternative(payload.html_body, subtype="html")
        return msg


def send_via_smtp(account, msg):
    settings = get_mail_settings()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(account.address, account.password)
        server.send_message(msg)


# Startup-time credential validation
def validate_mail_credentials() -> dict[str, str]:
    """Attempt to login for each configured account. Returns map address->"ok" or error string."""
    results: dict[str, str] = {}
    settings = get_mail_settings()
    accounts = []
    if settings.accounts:
        accounts.extend(settings.accounts.values())
    if settings.schreiber:
        accounts.append(settings.schreiber)
    if not accounts:
        return {"_config": "no accounts configured"}
    for acc in accounts:
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(acc.address, acc.password)
            results[acc.address] = "ok"
        except Exception as exc:
            results[acc.address] = f"login failed: {exc}"
    return results

