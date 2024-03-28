import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
def send_verification_email(email, verification_token):
    sender_email = os.getenv("MAIL_FROM")
    receiver_email = email
    password = os.getenv("MAIL_PASSWORD")
    # Create the MIMEMultipart message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your Myntist Account Email"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the HTML version of your message
    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #F9F9F9;
            text-align: center;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #FFFFFF;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #333333;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        p {{
            color: #666666;
            font-size: 18px;
            margin-bottom: 30px;
        }}
        .verification-link {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #007BFF;
            color: #FFFFFF;
            font-size: 20px;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }}
        .verification-link:hover {{
            background-color: #0056B3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Verify your email</h1>
        <p>Copy the code to complete the registration for your Myntist Account</p>
        <h2>{verification_token}<h2>
    </div>
</body>
</html>
"""
    # Turn these into plain/html MIMEText objects
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    message.attach(part2)
    # Send the email
    try:
        with smtplib.SMTP_SSL(os.getenv("MAIL_SERVER"), os.getenv("MAIL_PORT")) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")







