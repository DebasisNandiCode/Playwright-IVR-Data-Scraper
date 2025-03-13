import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv


class SendEmails:
    """A class to send emails using SMTP"""

    # Load environment variables from .env file
    load_dotenv()

    # Secure sensitive data using environment variables
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_MIDDLEWARE_RECEIVER = os.getenv("EMAIL_MIDDLEWARE_RECEIVER")  # Corrected variable name

    # Raise an error if any variable is missing
    if not all([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_MIDDLEWARE_RECEIVER]):
        raise ValueError("Missing credentials! Please check the .env file.")

    @staticmethod   # No need to create an instance of SendEmails, just call SendEmails.send_email(...). Used SendEmails.EMAIL_USERNAME instead of self.EMAIL_USERNAME.
    # Function to send email
    def send_email(subject, body):
        sender_email = SendEmails.EMAIL_USERNAME
        receiver_email = SendEmails.EMAIL_MIDDLEWARE_RECEIVER

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # Attach email body (fixed issue here)
        message.attach(MIMEText(body, 'html'))

        # Setup email server
        try:
            with smtplib.SMTP('smtp.office365.com', 587) as server:
                server.starttls()
                server.login(sender_email, SendEmails.EMAIL_PASSWORD)
                server.sendmail(sender_email, receiver_email, message.as_string())
            
            print("Success! Email sent successfully.")

        except Exception as e:
            print(f"Oops! Failed to send email - {e}")




 # Example Usage
# if __name__ == "__main__":
#     SendEmails.send_email("Test Subject", "<h1>This is a test email</h1>")
