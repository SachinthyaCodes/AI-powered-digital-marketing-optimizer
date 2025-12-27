import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailService:
    @staticmethod
    def send_email(to_email, subject, html_content):
        """Send an email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = Config.MAIL_DEFAULT_SENDER
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                if Config.MAIL_USE_TLS:
                    server.starttls()
                
                # Login if credentials are provided
                if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                    server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(to_email, reset_token, user_name):
        """Send password reset email"""
        reset_link = f"{Config.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <p>We received a request to reset your password for your MarketMatic account. Click the button below to reset your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in 1 hour for security reasons.
                    </div>
                    
                    <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                    
                    <p>Best regards,<br>The MarketMatic Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 MarketMatic. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to_email=to_email,
            subject="Password Reset Request - MarketMatic",
            html_content=html_content
        )
