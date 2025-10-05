import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.admin_email = os.getenv('ADMIN_EMAIL', 'mockcrypto.test@gmail.com')
        self.admin_password = os.getenv('ADMIN_PASSWORD', 'jezu aiog mouz mmiv')
    
    def send_email(self, recipient_email, subject, body):
        if not self.admin_email or not self.admin_password:
            print("Admin email credentials not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables.")
            print(f"\nNotification (would be sent to {recipient_email}):")
            print(f"Subject: {subject}")
            print(f"Body: {body}\n")
            return False
        
        try:
            message = MIMEMultipart()
            message['From'] = self.admin_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            message.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.admin_email, self.admin_password)
                server.send_message(message)
            
            print(f"Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            print(f"\nNotification (failed to send to {recipient_email}):")
            print(f"Subject: {subject}")
            print(f"Body: {body}\n")
            return False
    
    def notify_transaction(
        self, 
        sender_email: Optional[str],
        receiver_email: Optional[str],
        from_address: str, 
        to_address: str, 
        amount_eth: float,
        sender_new_balance: float,
        receiver_new_balance: float,
        amount_usd: Optional[float] = None
    ):
        amount_str = f"{amount_eth:.6f} ETH"
        if amount_usd:
            amount_str += f" (${amount_usd:.2f} USD)"
        
        if sender_email:
            subject = "✅ Transaction Sent - Mock Web3 Wallet"
            body = f"""
Transaction Successful!

You have sent:
Amount: {amount_str}
From: {from_address}
To: {to_address}

Your new balance: {sender_new_balance:.6f} ETH

Thank you for using Mock Web3 Wallet!
"""
            self.send_email(sender_email, subject, body)
        
        if receiver_email:
            subject = "✅ Transaction Received - Mock Web3 Wallet"
            body = f"""
Transaction Successful!

You have received:
Amount: {amount_str}
From: {from_address}
To: {to_address}

Your new balance: {receiver_new_balance:.6f} ETH

Thank you for using Mock Web3 Wallet!
"""
            self.send_email(receiver_email, subject, body)
