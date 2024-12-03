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
    # print("HEADERS: ", request.headers)
    device_id = request.headers.get("device-id", None)
    user_id = request.headers.get("user-id", None)
    random_device_uuid = request.headers.get("random_device_uuid", None)
    device_identity_hash=request.headers.get("device_identity_hash", None)
    

    # Validate presence of device_id
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

    if device_identity_hash != generate_device_hash_for_validation(
        user_id=user_id, device_id=device_id, random_device_uuid=random_device_uuid
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_payload(message="Unauthorized user."),
        )

    # Additional checks (e.g., account status)
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
    device_identity_hash=websocket.headers.get("device_identity_hash", None)
    
    if not device_id:
        print("1---------------------------")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # return False
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail=get_payload(message="Device ID is required in headers."),
        # )

    # Fetch account details and validate device_id
    accounts_details = await db["accounts"].find_one(
        {"device_info.device_id": device_id}
    )
    if not accounts_details:
        print("2---------------------------")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # return False
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail=get_payload(message="Device not registered."),
        # )

    # Check if the device_id matches the generated one
    if device_identity_hash != generate_device_hash_for_validation(
        user_id=user_id, device_id=device_id, random_device_uuid=random_device_uuid
    ):
        print("3---------------------------")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # return False
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail=get_payload(message="Unauthorized user."),
        # )

    # Additional checks (e.g., account status)
    if not accounts_details.get("is_activated", False):
        print("4---------------------------")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail=get_payload(message="Account is deactivated."),
        # )

    if not accounts_details.get("is_email_verified", False):

        print("5---------------------------")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail=get_payload(message="Email is not verified."),
        # )

    accounts_details["device_id"] = device_id
    return accounts_details
