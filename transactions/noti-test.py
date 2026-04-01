import firebase_admin
from firebase_admin import credentials, messaging
import random

# Path to your Firebase service account JSON file
SERVICE_ACCOUNT_PATH = "firebase.json"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# FCM Token and Notification Details
# fcm_token = "f9-9YVRl39vH3hYsg_3iXl:APA91bH7tTSKANGJ2y0OV0OZuabc-_8UReWBy5_q48q3R2OO0aywhKr_I4xnUH1C3FrcPssvTCDxPrAvwI9mo03FLXszlT6RcwJG_OWccv-cw5xu6yI2ukI"
fcm_token = "c7GaZqZTY_QAWcNMZUg-5O:APA91bE6ki69e6qWYJr2ossWXC8yJ1P4TkTvRsoriR2wNGYRRy0FN9VTYz2MZ-cspnGSU5qPBgMwX9IItfwOleXkqT4bA8X8Z42_qDz6eRrIyzf9gZjKNHo"
notification_title = f"Test Notification : {random.randint(1,9999999)}"
notification_body = "This is a test message sent via Firebase Cloud Messaging."
admin_url = "https://binance-trade.up.railway.app"

# Create the message
message = messaging.Message(
    notification=messaging.Notification(
        title=notification_title,
        body=notification_body,
    ),
    data={
        "admin_url": admin_url,  # Additional data payload
    },
    token=fcm_token,
)

# Send the message
try:
    response = messaging.send(message)
    print(f"Successfully sent message: {response}")
except Exception as e:
    print(f"Error sending message: {e}")
