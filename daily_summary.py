# daily_summary.py

import requests
import datetime
from textblob import TextBlob
from bs4 import BeautifulSoup
import json

KEYWORDS = ["bitcoin", "btc", "crypto", "fed", "inflation", "regulation"]
NEWS_SOURCES = [
    "https://www.reuters.com/markets/cryptocurrencies/",
    "https://cointelegraph.com/",
    "https://www.coindesk.com/",
    "https://www.bloomberg.com/crypto",
    "https://decrypt.co/",
    "https://cryptobriefing.com/"
]

DAILY_WEBHOOK = "https://discordapp.com/api/webhooks/1399659709891608649/NmETlG03Owk-7vmvIPkCfQTGTT3EqCSRlnAuZRN8QNbwKyo2P2o2IdjynmgP4cyYeFnq"

def fetch_headlines():
    headlines = []
    for url in NEWS_SOURCES:
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['h1', 'h2', 'h3']):
                text = tag.get_text().strip()
                if any(keyword in text.lower() for keyword in KEYWORDS):
                    headlines.append(text)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
    return headlines

def analyze_sentiment(headlines):
    scores = []
    for h in headlines:
        blob = TextBlob(h)
        scores.append(blob.sentiment.polarity)
    avg = sum(scores) / len(scores) if scores else 0
    trend = "↗️ Upward" if avg > 0.15 else "↘️ Downward" if avg < -0.15 else "→ Stable"
    return avg, trend, sorted(headlines, key=lambda h: abs(TextBlob(h).sentiment.polarity), reverse=True)[:3]

def send_discord_summary(avg, trend, top_headlines):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    content = f"📊 **Daily Crypto Sentiment Summary ({now})**\n"
    content += f"**Average Sentiment Score:** {avg:.3f}\n"
    content += f"**Trend:** {trend}\n"
    content += "\n**Top 3 Headlines:**\n" + "\n".join([f"- {h}" for h in top_headlines])
    payload = {"content": content}
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(DAILY_WEBHOOK, data=json.dumps(payload), headers=headers)
        print("Summary sent to Discord.")
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

if __name__ == "__main__":
    headlines = fetch_headlines()
    avg, trend, top = analyze_sentiment(headlines)
    send_discord_summary(avg, trend, top)
