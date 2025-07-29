import requests
from textblob import TextBlob
from bs4 import BeautifulSoup
import datetime
import json

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

DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1399659709891608649/NmETlG03Owk-7vmvIPkCfQTGTT3EqCSRlnAuZRN8QNbwKyo2P2o2IdjynmgP4cyYeFnq"

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
            print(f"Error fetching {url}: {e}")
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

def send_discord_notification(message):
    payload = {"content": message}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print("Discord message sent successfully.")
        else:
            print(f"Failed to send Discord message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception sending Discord message: {e}")

def format_daily_summary(score, headlines):
    emoji = "📈" if score > 0.15 else "📉" if score < -0.15 else "⚖️"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = (
        f"📊 **Daily Crypto Sentiment Summary**\n"
        f"🕗 `{now}`\n"
        f"{emoji} **24h Sentiment Score**: `{score:.3f}`\n"
        f"🧠 **Interpretation**: {'Bullish' if score > 0.15 else 'Bearish' if score < -0.15 else 'Neutral'}\n\n"
        f"📰 **Top 5 Headlines:**\n"
    )
    for h in headlines[:5]:
        summary += f"• {h}\n"
    return summary

if __name__ == "__main__":
    headlines = fetch_headlines()
    sentiment_score = analyze_sentiment(headlines)
    message = format_daily_summary(sentiment_score, headlines)
    send_discord_notification(message)
