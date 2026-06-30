import imaplib
import email
import time
import os
import requests

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

IMAP_SERVER = "imap.gmail.com"

KEYWORDS = {
    "Ton article s'est vendu !": "💸 Nouvelle vente Vinted !",
    "La transaction est finalisée": "💰 Transaction finalisée !",
    "Nous allons nous occuper de ton colis": "📦 Colis expédié !",
    "Ton colis arrive aujourd'hui": "🚚 Colis en livraison !",
    "Votre colis a été retiré": "✅ Colis reçu !"
}

seen = set()

def send_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def check_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")

    _, messages = mail.search(None, "ALL")
    mail_ids = messages[0].split()

    for mail_id in mail_ids[-20:]:
        if mail_id in seen:
            continue

        _, msg_data = mail.fetch(mail_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]

        if subject:
            for keyword, discord_msg in KEYWORDS.items():
                if keyword in subject:
                    send_discord(f"{discord_msg}\nSujet du mail : {subject}")
                    seen.add(mail_id)

    mail.logout()

while True:
    try:
        check_emails()
    except Exception as e:
        print("Erreur:", e)

    time.sleep(60)
