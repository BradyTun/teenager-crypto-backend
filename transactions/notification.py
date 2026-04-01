from django.conf import settings
from django.contrib.auth import get_user_model
import os

from firebase_admin import messaging
from firebase_admin import credentials
import firebase_admin

firebase_json_path = os.path.join(settings.BASE_DIR, "firebase.json")
cred = credentials.Certificate(firebase_json_path)
firebase_admin.initialize_app(cred)

User = get_user_model()

def send_notification_to_superusers(title, body, admin_url):
    """
    Send a notification to all superusers with a registered FCM token.
    """
    # Get superusers with valid FCM tokens
    superusers = User.objects.filter(is_superuser=True, fcm_registration_token__isnull=False)

    for superuser in superusers:
        # Create a notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={"admin_url": 'https://binance-trade.up.railway.app'+admin_url},  # Add admin panel link
            token=superuser.fcm_registration_token,
        )
        try:
            # Send the message
            res = messaging.send(message)
            print(f"Successfully sent message: {res}")

        except Exception as e:
            print(f"Failed to send notification to {superuser.email}: {e}")
            
            
