import snscrape.modules.twitter as sntwitter
import requests
import urllib.parse
import os

# ===== CONFIG =====
TWITTER_USER = "thatskygame"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = str(os.getenv("CHAT_ID"))

LAST_ID_FILE = "last_id.txt"
LAST_UPDATE_FILE = "last_update.txt"

# ===== FILE STORAGE =====
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
    try:
        scraper = sntwitter.TwitterUserScraper(TWITTER_USER)
        for tweet in scraper.get_items():
            return tweet
    except Exception as e:
        print("Erreur snscrape:", e)
    return None

# ===== TRADUCTION (simple gratuite) =====
def translate(text):
    replacements = {
        "Sky Kids": "Sky kids",
        "Sky kids": "Sky kids",
        "Season": "Saison",
        "Spirits": "Esprits",
        "Candle": "Bougie",
        "Winged Light": "Winged Light"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text

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

# ===== CHECK COMMANDES TELEGRAM =====
def check_commands():
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

# ===== AUTO CHECK =====
def auto_check():
    tweet = get_latest_tweet()

    if not tweet:
        print("Aucun tweet")
        return

    last_id = get_last_id()

    if tweet.id != last_id:
        print("Nouveau tweet détecté")
        translated = translate(tweet.content)
        send_telegram(tweet.content, translated)
        save_last_id(tweet.id)

# ===== MAIN =====
if __name__ == "__main__":
    print("Script lancé")

    check_commands()   # IMPORTANT : avant auto
    auto_check()
