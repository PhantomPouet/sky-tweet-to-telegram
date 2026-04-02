import snscrape.modules.twitter as sntwitter
import requests
import urllib.parse
import os

# ===== CONFIG =====
TWITTER_USER = "thatskygame"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_ID_FILE = "last_id.txt"
LAST_UPDATE_FILE = "last_update.txt"

# ===== GESTION FICHIERS =====
def get_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read())
    except:
        return None

def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))

def get_last_update():
    try:
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read())
    except:
        return None

def save_last_update(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))

# ===== TWITTER =====
def get_latest_tweet():
    for tweet in sntwitter.TwitterUserScraper(TWITTER_USER).get_items():
        return tweet

# ===== TRADUCTION GRATUITE (simple mais safe) =====
def translate(text):
    translated = text

    # mini adaptations Sky (tu peux enrichir)
    replacements = {
        "Sky Kids": "Sky kids",
        "Sky kids": "Sky kids",
        "Season": "Saison",
        "Spirits": "Espritss",
        "Candle": "Bougie",
        "Winged Light": "Winged Light"
        "Candle cake": "Gâtougie"
    }

    for k, v in replacements.items():
        translated = translated.replace(k, v)

    return translated

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

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "reply_markup": keyboard
        }
    )

# ===== SCAN AUTOMATIQUE =====
def auto_check():
    tweet = get_latest_tweet()
    last_id = get_last_id()

    if tweet and tweet.id != last_id:
        translated = translate(tweet.content)
        send_telegram(tweet.content, translated)
        save_last_id(tweet.id)

# ===== SCAN MANUEL VIA /scan =====
def check_manual_scan():
    last_update = get_last_update()

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(url).json()

    for update in response.get("result", []):
        update_id = update["update_id"]

        if last_update and update_id <= last_update:
            continue

        if "message" in update:
            text = update["message"].get("text", "").strip()
            chat_id = update["message"]["chat"]["id"]

            if str(chat_id) != str(CHAT_ID):
                continue

            if text == "/scan":
                tweet = get_latest_tweet()
                if tweet:
                    translated = translate(tweet.content)
                    send_telegram(tweet.content, translated)

        save_last_update(update_id)

# ===== MAIN =====
if __name__ == "__main__":
    try:
        auto_check()
        check_manual_scan()
    except Exception as e:
        print("Erreur:", e)
