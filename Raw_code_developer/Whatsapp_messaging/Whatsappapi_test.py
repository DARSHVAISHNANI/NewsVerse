from twilio.rest import Client

# Your credentials
account_sid = "AC1d5ab7898f9f098146c40cfff1a37a7c"
auth_token = "c205c6741c7d7db385d66a7d7470b956"
client = Client(account_sid, auth_token)

# WhatsApp sandbox number from Twilio
from_whatsapp = "whatsapp:+14155238886"
to_whatsapp = "whatsapp:+919375981112"

message = client.messages.create(
    from_=from_whatsapp,
    body="Hello! 🎉 Your Twilio WhatsApp setup is working!",
    to=to_whatsapp
)

print("Message SID:", message.sid)