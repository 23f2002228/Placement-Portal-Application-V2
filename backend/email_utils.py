from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

import config


def send_email(to_address, subject, message, content="text", attachment=None):
    if not to_address:
        return False

    msg = MIMEMultipart()
    msg["To"] = to_address
    msg["From"] = config.SENDER_EMAIL
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment:
        with open(attachment, "rb") as attachment_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())

        encoders.encode_base64(part)
        filename = os.path.basename(attachment)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    with smtplib.SMTP(host=config.SMTP_HOST, port=config.SMTP_PORT) as smtp:
        if config.SENDER_PASSWORD:
            smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        smtp.send_message(msg)

    return True
