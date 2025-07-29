import datetime
import requests
from discord_webhook import DiscordWebhook

# === CONFIGURATION ===
DAILY_SUMMARY_WEBHOOK = "https://discordapp.com/api/webhooks/1399651115032772669/gEFeifjhCiqHOPZkUjS8kv7QF3OY3NTqaNv77o3hhyxnh0pcg8AXBEOQnwqS8IfciEzQ"
SENTIMENT_LOG_PATH = "sentiment_log.json"  # where hourly sentiment records are stored
BREAKING_THRESHOLD = 0.75

# === FUNCTION TO LOAD SENTIMENT HISTORY ===
def load_sentiment_data():
    import json
    from pathlib import Path
    if not Path(SENTIMENT_LOG_PATH).exists():
        return []
    with open(SENTIMENT_LOG_PATH, 'r') as file:
        return json.load(file)

# === FUNCTION TO GENERATE SUMMARY ===
def generate_summary(data):
    now = datetime.datetime.utcnow()
    last_24 = [d for d in data if (now - datetime.datetime.fromisoformat(d['timestamp'])).total_seconds() <= 86400]
    if not last_24:
        return "No sentiment data available in the past 24 hours."

    scores = [d['score'] for d in last_24]
    avg_score = sum(scores) / len(scores)
    trend = "Up" if scores[-1] > scores[0] else "Down" if scores[-1] < scores[0] else "Flat"

    top_positive = sorted(last_24, key=lambda x: x['score'], reverse=True)[:3]
    top_negative = sorted(last_24, key=lambda x: x['score'])[:3]
    breaking = [d for d in last_24 if abs(d['score']) >= BREAKING_THRESHOLD]

    summary = f"**📊 Daily Sentiment Summary ({now.strftime('%Y-%m-%d')} UTC)**\n"
    summary += f"**Average Score:** {avg_score:.2f} | **Trend:** {trend}\n"

    summary += "\n**🔼 Top Positive News:**\n"
    for item in top_positive:
        summary += f"• `{item['score']:.2f}` — {item['headline']}\n"

    summary += "\n**🔽 Top Negative News:**\n"
    for item in top_negative:
        summary += f"• `{item['score']:.2f}` — {item['headline']}\n"

    if breaking:
        summary += "\n🚨 **Breaking Signals:**\n"
        for item in breaking:
            summary += f"• `{item['score']:.2f}` — {item['headline']}\n"

    return summary

# === FUNCTION TO SEND TO DISCORD ===
def send_to_discord(message):
    webhook = DiscordWebhook(url=DAILY_SUMMARY_WEBHOOK, content=message)
    response = webhook.execute()
    return response.status_code

# === MAIN ===
if __name__ == "__main__":
    data = load_sentiment_data()
    report = generate_summary(data)
    send_to_discord(report)
