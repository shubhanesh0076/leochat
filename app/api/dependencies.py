import random
import typing
from fastapi import status
from fastapi.requests import Request
from utils.helpers import get_payload
from fastapi.exceptions import HTTPException
from utils.security import generate_device_id, generate_device_hash_for_validation
from db.db_connection import get_database
from fastapi import HTTPException, Request, status, Depends
from fastapi.websockets import WebSocket


async def is_authenticated_user(
    request: Request,
    db: typing.Annotated[str, Depends(get_database)],
):
    device_id = request.headers.get("device-id", None)
    user_id = request.headers.get("user-id", None)
    random_device_uuid = request.headers.get("random_device_uuid", None)
    device_identity_hash = request.headers.get("device_identity_hash", None)

    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_payload(message="Device ID is required in headers."),
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_payload(message="User ID is required in headers."),
        )

    if not random_device_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_payload(message="Random device uuid ID is required in headers."),
        )

    # Fetch account details and validate device_id
    accounts_details = await db["accounts"].find_one(
        {"device_info.device_id": device_id}
    )
    if not accounts_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_payload(message="Device not registered."),
        )

    if str(accounts_details.get("user_id", None)) != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_payload(message="Invalid user id."),
        )

    if device_identity_hash != generate_device_hash_for_validation(
        user_id=user_id, device_id=device_id, random_device_uuid=random_device_uuid
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_payload(message="Unauthorized user."),
        )

    if not accounts_details.get("is_activated", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_payload(message="Account is deactivated."),
        )

    if not accounts_details.get("is_email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_payload(message="Email is not verified."),
        )

    accounts_details["device_id"] = device_id
    return accounts_details


async def is_authenticated_user_websocket(
    websocket: WebSocket,
    db: typing.Annotated[str, Depends(get_database)],
):
    device_id = websocket.headers.get("device-id", None)
    user_id = websocket.headers.get("user-id", None)
    random_device_uuid = websocket.headers.get("random_device_uuid", None)
    device_identity_hash = websocket.headers.get("device_identity_hash", None)

    # if not device_id or not user_id or not random_device_uuid:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    # Fetch account details and validate device_id
    accounts_details = await db["accounts"].find_one(
        {"device_info.device_id": device_id}
    )
    # if not accounts_details:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    # if str(accounts_details.get("user_id", None)) != user_id:
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    # if device_identity_hash != generate_device_hash_for_validation(
    #     user_id=user_id, device_id=device_id, random_device_uuid=random_device_uuid
    # ):
    #     print("HII.........", )
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    # if not accounts_details.get("is_activated", False):
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    # if not accounts_details.get("is_email_verified", False):
    #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    accounts_details["device_id"] = device_id
    return accounts_details
