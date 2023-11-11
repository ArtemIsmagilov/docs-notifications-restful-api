import aiosmtplib
from motor.motor_asyncio import AsyncIOMotorClientSession
from email.message import EmailMessage

from ..sql_app.crud import Notification
from ..schema import NotificationIn
from ..settings import SMTP_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD


async def only_send_email(user_email: str):
    msg = EmailMessage()

    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email
    msg["Subject"] = "Hello World!"
    msg.set_content('content')

    response = await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_LOGIN,
        password=SMTP_PASSWORD,
        use_tls=True,
    )

    return response
