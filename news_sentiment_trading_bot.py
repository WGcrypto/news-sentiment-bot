# news_sentiment_trading_bot.py

import requests
import time
from textblob import TextBlob
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.mime.text import MIMEText
import os
import json

# CONFIG
KEYWORDS = ["bitcoin", "btc", "crypto", "fed", "inflation", "regulation"]
NEWS_SOURCES = [
    "https://www.reuters.com/markets/cryptocurrencies/",
    "https://cointelegraph.com/",
    "https://www.coindesk.com/",
    "https://www.bloomberg.com/crypto",
    "https://decrypt.co/",
    "https://cryptobriefing.com/",
    "https://bitcoinist.com/",
    "https://www.investing.com/news/cryptocurrency-news",
    "https://www.fxstreet.com/cryptocurrencies",
    "https://news.bitcoin.com/",
    "https://cryptopotato.com/",
    "https://u.today/",
    "https://www.financemagnates.com/cryptocurrency/",
    "https://www.newsbtc.com/",
    "https://cryptoslate.com/",
    "https://ambcrypto.com/",
    "https://www.ccn.com/",
    "https://cryptobriefing.com/category/news/",
    "https://www.cryptonewsz.com/",
    "https://zycrypto.com/"
]
SENTIMENT_THRESHOLD = 0.15  # >0.15 bullish, <-0.15 bearish
FETCH_INTERVAL = 300  # seconds (5 mins)

# Load credentials from environment variables
EMAIL_FROM = os.getenv("EMAIL_USER")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_SUBJECT = "Trading Bot Signal"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_email_notification(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        server.quit()
        print("✅ Email sent.")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_discord_notification(message):
    payload = {"content": message}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print("✅ Discord message sent.")
        else:
            print(f"❌ Discord error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Discord exception: {e}")

def fetch_headlines():
    headlines = []
    for url in NEWS_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['h1', 'h2', 'h3']):
                text = tag.get_text().strip()
                if any(keyword in text.lower() for keyword in KEYWORDS):
                    headlines.append(text)
        except Exception as e:
            print(f"❌ Error fetching from {url}: {e}")
    return headlines

def analyze_sentiment(headlines):
    total_score = 0
    count = 0
    for h in headlines:
        blob = TextBlob(h)
        score = blob.sentiment.polarity
        total_score += score
        count += 1
    return total_score / count if count > 0 else 0

def make_decision(score):
    if score > SENTIMENT_THRESHOLD:
        return "BUY"
    elif score < -SENTIMENT_THRESHOLD:
        return "SELL"
    else:
        return "NEUTRAL"

def format_discord_message(sentiment, decision, headlines):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"📣 **Real-Time Crypto Alert**\n"
        f"🕒 `{time_now}`\n"
        f"🧠 **Sentiment Score**: `{sentiment:.3f}`\n"
        f"💡 **Suggested Action**: **{decision}**\n\n"
        f"📰 **Top Headlines:**\n"
    )
    for h in headlines[:5]:
        message += f"• {h}\n"
    return message

# Main loop
if __name__ == "__main__":
    while True:
        print(f"\n[{datetime.datetime.now()}] 📰 Checking crypto news...")
        headlines = fetch_headlines()
        sentiment = analyze_sentiment(headlines)
        decision = make_decision(sentiment)

        print(f"🧠 Sentiment Score: {sentiment:.3f} → Action: {decision}")

        body = f"Sentiment Score: {sentiment:.3f}\nSuggested Action: {decision}\n\nHeadlines:\n" + "\n".join(headlines[:10])
        send_email_notification(EMAIL_SUBJECT, body)

        discord_msg = format_discord_message(sentiment, decision, headlines)
        send_discord_notification(discord_msg)

        time.sleep(FETCH_INTERVAL)
