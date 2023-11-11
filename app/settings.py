from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.environ['MONGO_URL']

APP_HOST = os.environ['APP_HOST']
APP_PORT = os.environ['APP_PORT']
SMTP_PORT = os.environ['SMTP_PORT']
SMTP_HOST = os.environ['SMTP_HOST']
SMTP_LOGIN = os.environ['SMTP_LOGIN']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
SMTP_EMAIL = os.environ['SMTP_EMAIL']
