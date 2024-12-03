import re
import random
import uuid
from typing import Any, Optional
from utils import settings as st
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone


def get_payload(
    message: str = None,
    ok: bool = False,
    is_authenticated: bool = False,
    details: Any = None,
):
    payload = {
        "ok": ok,
        "is_authenticated": is_authenticated,
        "message": message,
        "details": details,
        "meta_info": {},
    }
    return payload


def validate_email(email: str) -> bool:
    """
    Validates an email address to ensure it follows the standard format.

    Parameters:
    ----------
    email : str
        The email address to validate.

    Returns:
    -------
    Optional[str]
        Returns the email address if valid, or raises a ValueError if invalid.

    Raises:
    ------
    ValueError:
        If the email address is invalid.
    """
    
    if re.match(st.EMAIL_REGEX, email):
        return True
    return False

def generate_otp(length=6):
    """
    Generate a unique integer code of the specified length.

    Parameters:
    ----------
    length : int
        The length of the unique code to generate. Default is 6.

    Returns:
    -------
    int
        A unique integer code.
    """
    if length < 1:
        raise ValueError("Length must be at least 1")
    
    lower_bound = 10**(length - 1)
    upper_bound = 10**length - 1

    return random.randint(lower_bound, upper_bound)

def generate_token(email: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=st.TOKEN_EXPIRATION_MINUTES)
    payload = {"email": email, "exp": expire}
    return jwt.encode(payload, st.SECRET_KEY, algorithm=st.ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, st.SECRET_KEY, algorithms=[st.ALGORITHM])
        return payload["email"]
    except ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except JWTError:
        raise ValueError("Invalid token.")
