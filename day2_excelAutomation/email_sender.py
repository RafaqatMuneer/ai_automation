from dotenv import load_dotenv
import os
from pathlib import Path
import yagmail
from typing import Optional
# path to .env file
env_path = Path(r"E:\python_programming\ai_automation\.env")
# Load .env file
load_dotenv(dotenv_path=env_path)
# email = os.getenv("EMAIL")
# password = os.getenv("GMAIL_PASSWORD")
class SendEmail:
    def __init__(self, email : str = os.getenv("EMAIL"), password : str = os.getenv("GMAIL_PASSWORD")) -> None:
        """
        Initialize the EmailSender with credentials.

        :param email: Sender's email address
        :param password: Sender's email password or app-specific password
        """
        self.email = email
        self.password =  password
        self.yag = yagmail.SMTP(self.email, self.password)
    def send_email(self, recipient_email:str, subject:str, body : str, attachment_path : Optional[str] = None) -> None:
        """
        Send an email with an optional attachment.

        :param recipient_email: The recipient's email address
        :param subject: The subject of the email
        :param body: The body of the email
        :param attachment_path: Optional path to an attachment
        """
        try:
        
            self.yag.send(
                to= recipient_email,
                subject=subject,
                contents=body,
                attachments=attachment_path,
            )
            # print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
if __name__ == "__main__":
    sender = SendEmail()
    sender.send_email(
        recipient_email= "faqi2023@gmail.com",
        subject="Progress Report",
        body="Please find attachment",
        attachment_path="Sales_Report.xlsx",
    )
        

