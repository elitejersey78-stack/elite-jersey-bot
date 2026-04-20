import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VERIFY_TOKEN = "elitejersey2024"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

FAQ = {
    "prix": "Bonjour ! Nos maillots sont disponibles à partir de 29,99€. Consultez notre site pour voir tous les prix 👉 [lien]",
    "livraison": "Bonjour ! La livraison prend 5 à 10 jours ouvrés. La livraison est gratuite à partir de 50€ d'achat 🚚",
    "taille": "Bonjour ! Nous avons les tailles S, M, L, XL et XXL. N'hésitez pas à consulter notre guide des tailles sur le site 📏",
    "retour": "Bonjour ! Vous avez 30 jours pour retourner un article. Contactez-nous par mail pour initier un retour 📦",
    "paiement": "Bonjour ! Nous acceptons carte bancaire, PayPal et Apple Pay 💳",
    "stock": "Bonjour ! Pour vérifier la disponibilité d'un article précis, dites-nous lequel vous cherchez 🔍",
}

DEFAULT = "Bonjour ! Merci pour votre message 😊 Pour toute question, vous pouvez aussi nous contacter par mail. Nous répondrons dès que possible !"

def get_response(message):
    message = message.lower()
    for keyword, response in FAQ.items():
        if keyword in message:
            return response
    return DEFAULT

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        for entry in data.get("entry", []):
            for msg in entry.get("messaging", []):
                sender_id = msg["sender"]["id"]
                message_text = msg.get("message", {}).get("text", "")
                if message_text:
                    reply = get_response(message_text)
                    requests.post(
                        f"https://graph.facebook.com/v19.0/me/messages",
                        params={"access_token": ACCESS_TOKEN},
                        json={"recipient": {"id": sender_id}, "message": {"text": reply}}
                    )
    except Exception as e:
        print(f"Erreur: {e}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
