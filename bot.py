import snscrape.modules.twitter as sntwitter
import requests
import urllib.parse
import os

# ===== CONFIG =====
TWITTER_USER = "thatskygame"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = str(os.getenv("CHAT_ID"))

LAST_UPDATE_FILE = "last_update.txt"

# ===== TELEGRAM =====
def send_telegram(original, translated):
    encoded = urllib.parse.quote(translated)
    twitter_url = f"https://twitter.com/compose/tweet?text={encoded}"

    message = f"🇬🇧 {original}\n\n🇫🇷 {translated}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🐦 Ouvrir X", "url": twitter_url}
            ]
        ]
    }

    print("Envoi Telegram...")

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "reply_markup": keyboard
        }
    )

# ===== TWITTER =====
def get_latest_tweet():
    try:
        tweets = list(sntwitter.TwitterUserScraper(TWITTER_USER).get_items())
        if tweets:
            print("Tweet trouvé")
            return tweets[0]
    except Exception as e:
        print("Erreur snscrape:", e)

    print("Aucun tweet récupéré")
    return None

# ===== TRADUCTION SIMPLE (améliorée gratuite) =====
def translate(text):
    print("Traduction...")

    # mini adaptation FR lisible
    replacements = {
        "is live": "est disponible",
        "is now live": "est maintenant disponible",
        "coming soon": "arrive bientôt",
        "starts now": "commence maintenant",
        "new Season": "nouvelle Saison",
        "Sky Kids": "Sky kids",
        "Sky kids": "Sky kids"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text

# ===== COMMANDES TELEGRAM =====
def get_last_update():
    try:
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read())
    except:
        return None

def save_last_update(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))

def check_commands():
    print("Check commandes...")

    last_update = get_last_update()

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(url).json()

    for update in response.get("result", []):
        update_id = update["update_id"]

        if last_update and update_id <= last_update:
            continue

        if "message" in update:
            text = update["message"].get("text", "").strip()
            chat_id = str(update["message"]["chat"]["id"])

            if chat_id != CHAT_ID:
                continue

            print("Commande reçue:", text)

            if text == "/scan":
                tweet = get_latest_tweet()
                if tweet:
                    translated = translate(tweet.content)
                    send_telegram(tweet.content, translated)

        save_last_update(update_id)

# ===== AUTO (TOUJOURS ENVOYER POUR SIMPLIFIER) =====
def auto_check():
    print("Auto check...")

    tweet = get_latest_tweet()

    if not tweet:
        return

    translated = translate(tweet.content)
    send_telegram(tweet.content, translated)

# ===== MAIN =====
if __name__ == "__main__":
    print("Script lancé")

    check_commands()
    auto_check()
