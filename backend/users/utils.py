import random
from django.core.mail import EmailMessage, get_connection
from .models import User, OnetimePassword
from django.conf import settings
from decouple import config

def generateOtp():
    otp=""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp


def send_code_to_user(email):
    Subject = "Crafitori Email Verification"
    otp_code = generateOtp()
    user = User.objects.get(email=email)
    site = "Crafitori"
    email_body = f"Hi {user.first_name} thanks for signing up on {site} please verify your email with the one time password {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    OnetimePassword.objects.create(user=user, code=otp_code)

    d_email = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    d_email.send(fail_silently=True)


from django.core.mail import EmailMessage, get_connection
from django.conf import settings

def resend_email(email):
    subject = "DentiaPro Email Verification"
    otp_code = generateOtp()
    user = User.objects.get(email=email)
    OnetimePassword.objects.create(user=user, code=otp_code)
    site = "DentiaPro"
    from_email = "noreply@crafitori.com"
    message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f6f6f6;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                max-width: 600px;
                margin: 0 auto;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #333333;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                color: #555555;
                font-size: 16px;
                line-height: 1.6;
            }}
            .otp-code {{
                font-weight: bold;
                font-size: 20px;
                color: #007BFF;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #999999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to {site}, {user.first_name}!</h1>
            <p>Thank you for signing up on {site}. To complete your registration, please verify your email address using the one-time password (OTP) provided below:</p>
            <p class="otp-code">{otp_code}</p>
            <p>If you did not sign up for an account, please disregard this email.</p>
            <p class="footer">Best regards,<br>{site} Team</p>
        </div>
    </body>
    </html>
    """

    with get_connection(
        host=settings.RESEND_SMTP_HOST,
        port=settings.RESEND_SMTP_PORT,
        username=settings.RESEND_SMTP_USERNAME,
        password=config("RESEND_API_KEY"),
        use_tls=True,
    ) as connection:
        email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[email],
            connection=connection,
        )
        email_message.content_subtype = "html"  # Set the content type to HTML
        email_message.send()



def send_normal_email(data):
    from_email = "noreply@crafitori.com"
    with get_connection(
        host=settings.RESEND_SMTP_HOST,
        port=settings.RESEND_SMTP_PORT,
        username=settings.RESEND_SMTP_USERNAME,
        password=config("RESEND_API_KEY"),
        use_tls=True,
    ) as connection:
        email=EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            from_email=from_email,
            to=[data['to_email']],
            connection=connection
        )
    email.send()
