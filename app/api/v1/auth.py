from fastapi import APIRouter, status
from utils.helpers import get_payload
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from schemas.auth import (
    UserRegisteration,
    ResentVerificationEmail,
    LoginWithCredentials,
    OTPVerifySchema,
    ContactsNo,
)
from fastapi.requests import Request
from pymongo.errors import DuplicateKeyError
from utils.security import (
    hash_password,
    is_authenticated,
    generate_device_id,
    combined_device_info,
)
from utils.emails import simple_mailer
from utils import settings as st
from utils.helpers import generate_token, generate_otp, verify_token
from datetime import datetime, timedelta, timezone
from api.dependencies import is_authenticated_user
from fastapi import Depends

# from utils.security import get_random_uuid

accounts = APIRouter(tags=["Accounts"])


@accounts.post(
    "/register",
    description="""
    Handles user registration.

    This endpoint allows users to register by providing their details such as name, email, password, 
    and mobile number. The password is hashed before storing the data in the database. Upon successful 
    registration, a verification email is sent to the user's email address for account activation.

    Body Parameters:
    -----------
    "email (Required, str)": "The user's email address.",
    "mobile_no ((Required, str))": "string",
    "password (Required, str)": "User password.",
    "confirm_password (Required, str)": "confirm user password.",
    
    Example:
    --------
    Method: POST /api/v1/auth
    Body: 
        {
            "email": "johndoe@example.com",
            "mobile_no": "1234567890"
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
    """,
)
async def register_user(request: Request, user_registeration: UserRegisteration):
    """
    Handles user registration.

    This endpoint allows users to register by providing their details such as name, email, password,
    and mobile number. The password is hashed before storing the data in the database. Upon successful
    registration, a verification email is sent to the user's email address for account activation.

    Body Parameters:
    -----------
    "email (Required, str)": "The user's email address.",
    "mobile_no ((Required, str))": "string",
    "password (Required, str)": "User password.",
    """

    db = request.app.db
    user_collection = db["accounts"]
    deserialized_user_data = user_registeration.model_dump()

    try:
        del deserialized_user_data["confirm_password"]
        deserialized_user_data["password"] = hash_password(
            deserialized_user_data["password"]
        )

        # Generate verification token and OTP
        deserialized_user_data["email_verification_token"] = generate_token(
            email=deserialized_user_data["email"]
        )
        deserialized_user_data["email_verification_otp"] = generate_otp()

        # Insert the user data.
        await user_collection.insert_one(deserialized_user_data)

        # get the user data.
        user_data = await user_collection.find_one(
            {"email": deserialized_user_data["email"]}
        )

        if user_data:
            scheme = request.url.scheme  # http or https
            host = request.client.host  # Client host (IP address)
            port = request.url.port
            link = f"{scheme}://{host}:{port}/api/v1/auth/verify-email?token={user_data['email_verification_token']}"
            print("LINK: ", link)
            simple_mailer(
                template_file=st.REGISTERATION_EMAIL_TEMPLATE,
                context={"user_data": user_data, "link": link},
                to_emails=[user_data["email"]],
                subject="Welcome To Leo Chat.",
            )
            payload = get_payload(
                message=f"Account has been created and send the 6 digit code for account verification at your registered email: {user_data['email']}",
                ok=True,
            )
            return JSONResponse(content=payload, status_code=status.HTTP_201_CREATED)

    except DuplicateKeyError as dke:
        if "email" in str(dke):
            return JSONResponse(
                content=get_payload(message="Email already registered, "),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif "mobile_no" in str(dke):
            return JSONResponse(
                content=get_payload("Mobile number already registered."),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return JSONResponse(
                content=get_payload("Duplicate entry detected."),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        payload = get_payload(message=f"An un-expected error occurse: {e}")
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@accounts.post("/resend-verification-email")
async def resend_email(
    request: Request, resend_verification_email: ResentVerificationEmail
):
    db = request.app.db
    user_collection = db["accounts"]

    # Extract email from the request
    email = resend_verification_email.email
    user_data = await user_collection.find_one({"email": email})

    # Check if the user exists
    if not user_data:
        return JSONResponse(
            content=get_payload(message="The provided email does not exist."),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Check if the account is already verified
    if user_data.get("is_email_verified", False):
        return JSONResponse(
            content=get_payload(
                message="Your account is already verified. No need to resend the verification email."
            ),
            status_code=status.HTTP_409_CONFLICT,
        )

    # Update the user's verification token and OTP
    try:
        verification_token = generate_token(email=email)
        verification_otp = generate_otp()
        await user_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "email_verification_token": verification_token,
                    "email_verification_otp": verification_otp,
                }
            },
        )
    except Exception as e:
        return JSONResponse(
            content=get_payload(
                message=f"An unexpected error occurred while updating the database: {e}"
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Send the verification email
    try:
        scheme = request.url.scheme  # http or https
        host = request.client.host  # Client host (IP address)
        port = request.url.port
        link = f"{scheme}://{host}:{port}/api/v1/auth/verify-email?token={verification_token}"
        print("LINK: ", link)
        simple_mailer(
            template_file=st.REGISTERATION_EMAIL_TEMPLATE,
            context={"user_data": user_data, "link": link},
            to_emails=[email],
            subject="Welcome To Leo Chat.",
        )
    except Exception as e:
        return JSONResponse(
            content=get_payload(
                message=f"Failed to send email. An error occurred: {e}"
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Success response
    return JSONResponse(
        content=get_payload(
            message=f"Verification email has been sent successfully to: {email}.",
            ok=True,
        ),
        status_code=status.HTTP_200_OK,
    )


@accounts.get("/verify-email")
async def verify_email(request: Request, token: str):
    db = request.app.db
    user_collection = db["accounts"]

    try:
        email = verify_token(token)
        if not email:
            raise ValueError("Invalid or expired token")

    except ValueError as ve:
        payload = get_payload(message=f"{ve}")
        return JSONResponse(content=payload, status_code=status.HTTP_400_BAD_REQUEST)

    user = await user_collection.find_one({"email": email})
    if not user:
        payload = get_payload(message=f"User not found")
        return JSONResponse(content=payload, status_code=status.HTTP_404_NOT_FOUND)

    if user.get("is_email_verified", False):
        message = "Account has been already verified."
        payload = get_payload(message=message)
        return JSONResponse(content=payload, status_code=status.HTTP_409_CONFLICT)

    # Update user as verified
    filter = {"email": email}
    update = {
        "$set": {
            "is_email_verified": True,
            "is_activated": True,
            "email_verification_token": None,
        }
    }
    try:
        await user_collection.update_one(filter, update)
        message = "Account has been successfully verified."

    except Exception as e:
        message = f"An un expected error Occurse: {e}"
        payload = get_payload(message=message)
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    payload = get_payload(message=message, ok=True)
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@accounts.post("/login-with-credentials")
async def login_with_credentials(
    request: Request, login_with_credentials: LoginWithCredentials
):
    db = request.app.db
    user_collection = db["accounts"]
    deserialized_user_credentials = login_with_credentials.model_dump()

    user_data = await user_collection.find_one(
        {"email": deserialized_user_credentials["email"]}
    )
    if not user_data:
        payload = get_payload(message="User does not exists.")
        return JSONResponse(content=payload, status_code=status.HTTP_404_NOT_FOUND)

    if not is_authenticated(user_data, deserialized_user_credentials):
        payload = get_payload(message="Invalid Credentials.")
        return JSONResponse(content=payload, status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        # Generate a pseudo Device ID using a hash
        device_info = combined_device_info(
            request, user_data["email"]
        )
        device_info["is_logged_in"] = True
        
        # Update the device info if `device_id` exists, otherwise push a new entry
        result = await user_collection.update_one(
            {
                "email": user_data["email"],
                "device_info.device_id": device_info["device_id"],
            },
            {"$set": {"device_info.$": device_info}},  # Update the matching device info
        )

        # If no device was updated, push the new device info
        if result.matched_count == 0:
            await user_collection.update_one(
                {"email": user_data["email"]},
                {"$push": {"device_info": device_info}},
            )

    except Exception as e:
        payload = get_payload(message=f"An un-expected error Occurse: {e}")
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    payload = get_payload(
        message="Logged-in successfully",
        ok=True,
        details={
            "device_info": device_info,
            "email": user_data["email"],
            "user_id": f"{user_data['user_id']}",
        },
    )
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@accounts.post("/sent-login-otp")
async def login_with_otp(request: Request, login: ResentVerificationEmail):

    db = request.app.db
    user_collection = db["accounts"]

    login_dict = login.model_dump()
    email = login_dict.get("email", None)

    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        payload = get_payload(message="User does not exists.")
        return JSONResponse(content=payload, status_code=status.HTTP_404_NOT_FOUND)

    # Generate and save OTP with expiration
    otp = generate_otp()
    otp_expiration = datetime.now(tz=timezone.utc) + timedelta(
        minutes=st.OTP_EXPIRATION_MINUTES
    )

    # Update `user_data` in memory to avoid fetching it again
    user_data["otp"] = {
        "otp": {
            "login_otp": otp,
            "login_otp_expiration": otp_expiration,
        }
    }
    print("OTP................ ", otp)
    await user_collection.update_one(
        {"email": user_data["email"]},
        {"$set": user_data["otp"]},
    )
    # Send OTP via email
    try:
        simple_mailer(
            template_file=st.OTP_EMAIL_TEMPLATE,
            context={
                "user_data": user_data["otp"],
                "otp_expiry_min": st.OTP_EXPIRATION_MINUTES,
            },
            to_emails=[email],
            subject="Login OTP.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {e}",
        )

    payload = get_payload(
        message=f"OTP sent to your registered email: {user_data['email']} ", ok=True
    )
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


@accounts.post("/verify-otp")
async def verify_otp(request: Request, otp_verify: OTPVerifySchema):

    db = request.app.db
    user_collection = db["accounts"]

    otp_verify = otp_verify.model_dump()
    user_data = await user_collection.find_one({"email": otp_verify["email"]})

    if not user_data:
        payload = get_payload(message="User not found")
        return JSONResponse(content=payload, status_code=status.HTTP_404_NOT_FOUND)

    if otp_verify["login_otp"] != user_data["otp"]["login_otp"]:
        message = "Invalid OTP"
        payload = get_payload(message=message)
        return JSONResponse(content=payload, status_code=status.HTTP_400_BAD_REQUEST)

    if datetime.now(tz=timezone.utc) > datetime.strptime(
        f"{user_data['otp']['login_otp_expiration']}", st.TZ_OFFSET_FORMAT
    ).replace(tzinfo=timezone.utc):
        message = "OTP Expired."
        payload = get_payload(message=message)
        return JSONResponse(content=payload, status_code=status.HTTP_400_BAD_REQUEST)

    # Generate a pseudo Device ID using a hash
    device_id = generate_device_id(request, user_data["email"])

    try:
        # Generate a pseudo Device ID using a hash
        device_info = combined_device_info(request, user_data["email"])
        device_info["is_logged_in"] = True

        # Update the device info if `device_id` exists, otherwise push a new entry
        result = await user_collection.update_one(
            {
                "email": user_data["email"],
                "device_info.device_id": device_info["device_id"],
            },
            {"$set": {"device_info.$": device_info}},  # Update the matching device info
        )

        # If no device was updated, push the new device info
        if result.matched_count == 0:
            await user_collection.update_one(
                {"email": user_data["email"]},
                {"$push": {"device_info": device_info}},
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Device ID is not update in User account, has some issue: {e}",
        )

    payload = get_payload(
        message="Logged-in successfully",
        ok=True,
        details={
            "device_info": device_info,
            "email": user_data["email"],
            "user_id": f"{user_data['user_id']}",
        },
    )
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


# Helper Function to Check for Duplicates
def check_duplicate_email(contact_details_ls: list[dict], email: str) -> bool:
    if contact_details_ls:
        for contact in contact_details_ls:
            if contact["email"] == email:
                return True
    return False


@accounts.post("/add-contacts")
async def add_contact(
    request: Request,
    contacts_no: ContactsNo,
    account_details=Depends(is_authenticated_user),
):

    db = request.app.db
    user_collection = db["accounts"]
    contact_details = contacts_no.model_dump()
    filter = {"email": account_details["email"]}
    _update = {"$push": {"contacts_info": contact_details}}

    contact_info_ls = account_details.get("contacts_info", [])
    if check_duplicate_email(contact_info_ls, contact_details["email"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_payload(message="This email already exists in contact list."),
        )

    try:
        await user_collection.update_one(filter, _update)
        payload = get_payload(message="Contact added successfully.", ok=True)
        return JSONResponse(content=payload, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        payload = get_payload(message=f"An un-expected error Occurse: {e}")
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@accounts.post("/update-contact-details/{contact}")
async def update_contact_detail(
    request: Request,
    contacts_no: ContactsNo,
    account_details=Depends(is_authenticated_user),
):

    db = request.app.db
    user_collection = db["accounts"]
    contact_details = contacts_no.model_dump()
    filter = {"email": account_details["email"]}
    _update = {"$push": {"contacts_info": contact_details}}

    contact_info_ls = account_details.get("contacts_info", [])
    if check_duplicate_email(contact_info_ls, contact_details["email"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_payload(message="This email already has in this contact list."),
        )

    try:
        await user_collection.update_one(filter, _update)
        payload = get_payload(message="Contacted added successfully.", ok=True)
        return JSONResponse(content=payload, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        payload = get_payload(message=f"An un-expected error Occurse: {e}")
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
