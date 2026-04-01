import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_HOST = "smtp.maileroo.com"
EMAIL_PASSWORD = "be14c02d67716a79b8e22a85"
EMAIL_PORT = 587
EMAIL_USER = "noreply@cryptotradings.website"

# Test email details
recipient_email = "kyawkokotunmm475157@gmail.com"  # Replace with the recipient's email
subject = "Test Email"
body = "Hello, this is a test email sent using Python!"

def send_email():
    try:
        # Create email message
        message = MIMEMultipart()
        message["From"] = EMAIL_USER
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Secure the connection
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        # Send email
        server.sendmail(EMAIL_USER, recipient_email, message.as_string())
        print("Email sent successfully!")
        
        # Close the connection
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
