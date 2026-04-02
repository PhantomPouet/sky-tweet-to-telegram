import snscrape.modules.twitter as sntwitter
import requests
import urllib.parse
import os

TWITTER_USER = "thatskygame"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_ID_FILE = "last_id.txt"

def get_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read())
    except:
        return None

def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))

def get_latest_tweet():
    for tweet in sntwitter.TwitterUserScraper(TWITTER_USER).get_items():
        return tweet

def translate(text):
    # version gratuite simple
    return text.replace("Sky Kids", "Sky kids")  # exemple mini

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

tweet = get_latest_tweet()
last_id = get_last_id()

if tweet and tweet.id != last_id:
    translated = translate(tweet.content)
    send_telegram(tweet.content, translated)
    save_last_id(tweet.id)
