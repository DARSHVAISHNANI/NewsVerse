# in whatsapp_recommender/whatsapp_service.py

from twilio.rest import Client
from Whatsapp_Messaging import config

# Initialize the Twilio client once when the module is imported
try:
    twilio_client = Client(config.ACCOUNT_SID, config.AUTH_TOKEN)
    print("✅ Twilio client initialized successfully.")
except Exception as e:
    twilio_client = None
    print(f"❌ Failed to initialize Twilio client: {e}")

def formatMessage(news_article: dict) -> str:
    """Formats a news article dictionary into a readable WhatsApp message."""

    # Safely get nested data with defaults
    summary = news_article.get('summarization', {}).get('summary', 'No summary available.')
    fact_check = '✅ Verified' if news_article.get('fact_check', {}).get('llm_verdict', False) else '❌ Not Verified'
    sentiment = news_article.get('sentiment', 'N/A')
    date = news_article.get('date', 'N/A')
    source = news_article.get('source', 'N/A')
    url = news_article.get('url', '#')
    title = news_article.get('title', 'No Title')

    return f"""
📰 *Big News:* {title}

👉 {summary}

📌 *Fact-Check:* {fact_check}
😊 *Sentiment:* {sentiment}

📅 {date} | Source: {source}
🔗 Full story: {url}
"""

def sendWhatsapp(user_number: str, message: str):
    """Sends a message to a given user's WhatsApp number."""
    if not twilio_client:
        print("  - ⚠️  Cannot send message: Twilio client is not available.")
        return

    # --- FIX: Ensure the FROM number has the correct 'whatsapp:' prefix ---
    from_number = config.FROM_WHATSAPP
    if not from_number.lower().startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"
    # --- END FIX ---

    try:
        twilio_client.messages.create(
            from_=from_number, # Use the guaranteed correctly prefixed FROM number
            to=f"whatsapp:{user_number}",
            body=message
        )
    except Exception as e:
        print(f"  - ❌ Error sending message to {user_number}: {e}")