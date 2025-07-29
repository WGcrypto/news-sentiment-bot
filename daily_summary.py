import time
import requests
from datetime import datetime, timedelta
from textblob import TextBlob
from bs4 import BeautifulSoup

# ========== CONFIG ==========
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1399659709891608649/NmETlG03Owk-7vmvIPkCfQTGTT3EqCSRlnAuZRN8QNbwKyo2P2o2IdjynmgP4cyYeFnq"
NEWS_SOURCES = [
    "https://cryptopanic.com/news",  # Feel free to add more
]
NUM_HEADLINES = 3
# ============================

def fetch_headlines():
    headlines = []
    for source in NEWS_SOURCES:
        response = requests.get(source)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            if 30 < len(text) < 200:  # avoid clutter
                headlines.append(text)
        if len(headlines) >= 10:
            break
    return headlines[:15]

def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def summarize_sentiment():
    headlines = fetch_headlines()
    scored = [(h, analyze_sentiment(h)) for h in headlines]
    sorted_by_score = sorted(scored, key=lambda x: abs(x[1]), reverse=True)

    top = sorted_by_score[:NUM_HEADLINES]
    avg_score = sum(score for _, score in scored) / len(scored)
    trend = "⬆️ Bullish" if avg_score > 0.05 else "⬇️ Bearish" if avg_score < -0.05 else "➖ Neutral"

    summary = "**📰 Daily Crypto Sentiment Summary**\n\n"
    summary += f"**Trend:** {trend}\n"
    summary += f"**Avg Sentiment:** `{avg_score:.3f}`\n\n"
    summary += "**Top Headlines:**\n"
    for i, (h, s) in enumerate(top, 1):
        sentiment = "✅ Positive" if s > 0.1 else "⚠️ Negative" if s < -0.1 else "➖ Neutral"
        summary += f"{i}. {h}\n> Sentiment: `{s:.3f}` {sentiment}\n\n"
    return summary

def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    response.raise_for_status()

def sleep_until_8am():
    now = datetime.now()
    next_run = datetime.combine(now.date(), datetime.strptime("08:00", "%H:%M").time())
    if now >= next_run:
        next_run += timedelta(days=1)
    seconds_until = (next_run - now).total_seconds()
    print(f"[Scheduler] Sleeping for {int(seconds_until)} seconds until 8:00 AM...")
    time.sleep(seconds_until)

def run_daily_summary():
    try:
        print("[Bot] Fetching and analyzing sentiment...")
        summary = summarize_sentiment()
        print("[Bot] Sending to Discord...")
        send_to_discord(summary)
        print("[Bot] ✅ Summary sent.")
    except Exception as e:
        print(f"[Bot] ❌ Error: {e}")

if __name__ == "__main__":
    while True:
        run_daily_summary()
        sleep_until_8am()
