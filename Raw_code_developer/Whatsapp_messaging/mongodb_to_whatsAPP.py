from twilio.rest import Client
from pymongo import MongoClient

# Twilio credentials
ACCOUNT_SID = "AC1d5ab7898f9f098146c40cfff1a37a7c"
AUTH_TOKEN = "c205c6741c7d7db385d66a7d7470b956"
FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox or business number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Connect DB (MongoDB example)
mongo_client = MongoClient("mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/")
db = mongo_client["NewsVerseDB"]
collection = db["NewsVerseCo"]

def format_message(news):
    return f"""
📰 *Big News:* {news['title']}

👉 {news['summarization']['summary']}

📌 *Fact-Check:* {'✅ Verified' if news['fact_check']['verdict'] else '❌ Not Verified'}
😊 *Sentiment:* {news['sentiment']}

📅 {news['date']} | Source: {news['source']}
🔗 Full story: {news['url']}
"""

def send_whatsapp(user_number, message):
    client.messages.create(
        from_=FROM_WHATSAPP,
        to=f"whatsapp:{user_number}",
        body=message
    )

# Example pipeline
def push_news_to_user(user_number):
    news_item = collection.find_one(sort=[("date", -1)])  # latest news
    if news_item:
        msg = format_message(news_item)
        send_whatsapp(user_number, msg)

# Example usage
push_news_to_user("+919375981112")