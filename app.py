import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = "17841474792319225"

FAQ = {
    "prix": "Bonjour ! Nos maillots sont disponibles à partir de 29,99€. Consultez notre site pour voir tous les prix 👉 [lien]",
    "livraison": "Bonjour ! La livraison prend 5 à 10 jours ouvrés. La livraison est gratuite à partir de 50€ d'achat 🚚",
    "taille": "Bonjour ! Nous avons les tailles S, M, L, XL et XXL. Consultez notre guide des tailles sur le site 📏",
    "retour": "Bonjour ! Vous avez 30 jours pour retourner un article. Contactez-nous par mail pour initier un retour 📦",
    "paiement": "Bonjour ! Nous acceptons carte bancaire, PayPal et Apple Pay 💳",
    "stock": "Bonjour ! Pour vérifier la disponibilité d'un article précis, dites-nous lequel vous cherchez 🔍",
}

DEFAULT = "Bonjour ! Merci pour votre message 😊 Nous reviendrons vers vous dès que possible !"

answered = set()

def get_response(message):
    message = message.lower()
    for keyword, response in FAQ.items():
        if keyword in message:
            return response
    return DEFAULT

def send_message(recipient_id, text):
    requests.post(
        f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/messages",
        params={"access_token": ACCESS_TOKEN},
        json={"recipient": {"id": recipient_id}, "message": {"text": text}}
    )

def poll_messages():
    while True:
        try:
            res = requests.get(
                f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/conversations",
                params={
                    "access_token": ACCESS_TOKEN,
                    "fields": "participants,messages{message,from,created_time}"
                }
            )
            data = res.json()
            for conv in data.get("data", []):
                messages = conv.get("messages", {}).get("data", [])
                for msg in messages:
                    msg_id = msg.get("id")
                    sender_id = msg.get("from", {}).get("id")
                    text = msg.get("message", "")
                    if msg_id not in answered and sender_id != INSTAGRAM_ACCOUNT_ID and text:
                        answered.add(msg_id)
                        reply = get_response(text)
                        send_message(sender_id, reply)
        except Exception as e:
            print(f"Erreur polling: {e}")
        time.sleep(60)

@app.route("/")
def home():
    return "Bot actif ✅"

if __name__ == "__main__":
    thread = threading.Thread(target=poll_messages)
    thread.daemon = True
    thread.start()
    from gunicorn.app.base import BaseApplication
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
