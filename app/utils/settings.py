import os
from dotenv import load_dotenv

load_dotenv()

# DB VARIABLES
DB_USSERNAME: str = os.getenv("DB_USSERNAME")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")
RS_NAME: str = os.getenv("DB_NAME")
DB_URI: str = f"mongodb://{DB_USSERNAME}:{DB_PASSWORD}@leomongoPrimary:28021,leomongoSecondary:28022,leomongoTertiary:28023/?replicaSet={RS_NAME}&authMechanism=DEFAULT"

# EMAIL CONFIG VARIABLES.
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')
REGISTERATION_EMAIL_TEMPLATE="registeration_email.html"
OTP_EMAIL_TEMPLATE="otp_email.html"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
TZ_OFFSET_FORMAT="%Y-%m-%d %H:%M:%S.%f"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRATION_MINUTES = 15
OTP_EXPIRATION_MINUTES = 5