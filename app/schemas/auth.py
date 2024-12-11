from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field, field_validator
from utils.helpers import validate_email


class Accounts(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)  # Auto-generate UUID
    name: Optional[str] = None
    email: EmailStr
    mobile_no: str
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    profile_picture: Optional[UploadFile] = None
    about: Optional[str] = None
    is_activated: bool = False
    email_verification_otp: int = None
    is_email_verified: bool = False
    email_verification_token: str = None
    password: str
    confirm_password: str
    created_at: datetime = Field(
        default_factory=datetime.now
    )  # Auto-generate creation time
    updated_at: datetime = Field(
        default_factory=datetime.now
    )  # Auto-generate updated time

    class Config:
        json_schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "mobile_no": "1234567890",
                "password": "securepassword123",
                "confirm_password": "securepassword123",
                "dob": "",
                "gender": "",
                "age": "",
                "profile_picture": "",
                "about": "",
                "is_activated": "",
                "is_email_verified": "",
                "email_verification_token": "",
                "email_verification_otp": "",
                "otp": {
                    "login_otp": "otp", 
                    "login_otp_expiration": "otp_expiration"
                },
                "device_info": [
                    {
                        "device_name": "Unknown Device",
                        "os": "Other",
                        "browser": "PostmanRuntime",
                        "device_type": "Unknown",
                        "device_id": "cb3e3c85ef4c5f0969936aa6eb55095ce33dee353873d45c8270e028eefad0b8",
                        "is_logged_in": "In Bool "      
                    }
                ],
                "password": "",
                "confirm_password": "",
                "created_at": "",
                "updated_at": "",
                "contacts_info": [
                    {
                        "name": "",
                        "email": "",
                        "contact_no": "",
                        "has_account": "",
                        "added_at": ""
                    },
                    {
                        "name": "",
                        "email": "",
                        "contact_no": "",
                        "has_account": "",
                        "added_at": ""
                    }
                ]
            }
        }


class UserRegisteration(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)  # Auto-generate UUID
    email: EmailStr
    mobile_no: str
    password: str
    confirm_password: str
    created_at: datetime = Field(
        default_factory=datetime.now
    )  # Auto-generate creation time
    updated_at: datetime = Field(
        default_factory=datetime.now
    )  # Auto-generate updated time

    class Config:
        json_schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "mobile_no": "1234567890",
                "password": "securepassword123",
                "confirm_password": "securepassword123",
            }
        }

    @field_validator("confirm_password")
    def match_password_to_contirm_pass(cls, confirm_password, values):
        if confirm_password != values.data.get("password"):
            raise ValueError("Password do not not match.")
        return confirm_password


class ResentVerificationEmail(BaseModel):
    email: str

    @field_validator("email")
    def validate_email(cls, email):
        if not validate_email(email=email):
            raise ValueError("Invalid Email")
        return email


class LoginWithCredentials(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, email):
        if not validate_email(email=email):
            raise ValueError("Invalid Email")
        return email

class OTPVerifySchema(BaseModel):
    email: str
    login_otp: int
    
    @field_validator("email")
    def validate_email(cls, email):
        if not validate_email(email=email):
            raise ValueError("Invalid Email")
        return email
    

class ContactsNo(BaseModel):
    name: str
    email: str=None
    contact_no: str
    has_account: bool=False