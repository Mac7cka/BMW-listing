import smtplib
from email.message import EmailMessage
import os
import logging
import datetime


def send_email_with_attachment(deals, attachment_path):
    """ Sends an email with a list of car deals in the body and an Excel file attachment. """
    from_email = os.getenv("FROM_EMAIL")
    my_password = os.getenv("MY_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    today = datetime.datetime.now().strftime("%d.%m.%Y")

    if not deals:
        logging.warning("No deals found, skipping email.")
        return

    subject = f"🔥 New Car Deals - {today}"
    body = "Here are the latest car deals:\n\n"
    for deal in deals:
        body += (f"🚗 {deal['title']}\n📍 Location: {deal['location']}\n⛽ "
                 f"Fuel: {deal['fuel_type']}\n🔗 Link: {deal['link']}\n\n")

    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    if os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                file_data = attachment.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        except Exception as e:
            logging.error(f"Error attaching file: {e}")
            return
    else:
        logging.warning(f"Attachment file {attachment_path} not found. Sending email without attachment.")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, my_password)
            server.send_message(msg)
        logging.info(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")
