import json
from fastapi import APIRouter
from fastapi import Request
from utils.helpers import generate_room_id, convert_str_to_binary_uuid
from schemas.chat import ChatRoom, MessageModel
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from utils.helpers import get_payload
from fastapi import status
from api.dependencies import is_authenticated_user
from fastapi import Depends
from db.db_parser.parser import DBParsers
from db.redis.redis_connection import Redis

chat_room = APIRouter()


@chat_room.post("/create")
async def create_or_get_room(
    request: Request,
    chatroom: ChatRoom,
    account_details=Depends(is_authenticated_user),
):
    db = request.app.db
    chat_room_collection = db["chat_room"]

    # Deserialize and validate input
    chatroom_data = chatroom.model_dump()
    members = chatroom_data.get("members", [])

    # Validate members and collect their binary UUIDs
    members_ls = []
    for member_id in members:
        is_valid, binary_uuid = convert_str_to_binary_uuid(member_id)
        if not is_valid:
            return JSONResponse(
                content=get_payload(message=f"Invalid UUID for member: {member_id}"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the member exists in the accounts collection
        account_info = await db["accounts"].find_one({"user_id": binary_uuid})
        if not account_info:
            return JSONResponse(
                content=get_payload(message=f"User not found: {member_id}"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        members_ls.append(binary_uuid)

    # Generate a unique room ID
    room_id = generate_room_id(members)
    is_valid, binary_room_id = convert_str_to_binary_uuid(room_id[:32])
    if not is_valid:
        return JSONResponse(
            content=get_payload(message="Invalid generated room ID!"),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the chat room already exists
    existing_chat_room = await chat_room_collection.find_one(
        {"room_id": binary_room_id}
    )
    if existing_chat_room:
        return JSONResponse(
            content=get_payload(
                message="Chat Room already exists.",
                details={"room_id": str(existing_chat_room.get("room_id", None))},
            ),
            status_code=status.HTTP_200_OK,
        )

    # Create a new chat room
    try:
        chatroom_data.update({"room_id": binary_room_id, "members": members_ls})
        await chat_room_collection.insert_one(chatroom_data)

        return JSONResponse(
            content=get_payload(
                message="Chat Room created successfully.",
                ok=True,
                details={"room_id": str(binary_room_id.as_uuid())},
            ),
            status_code=status.HTTP_201_CREATED,
        )

    except DuplicateKeyError:
        return JSONResponse(
            content=get_payload(message="Chat Room already exists."),
            status_code=status.HTTP_409_CONFLICT,
        )

    except Exception as e:
        return JSONResponse(
            content=get_payload(message=f"Unexpected error occurred: {str(e)}"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@chat_room.get("/{room_id}/chats")
async def chat_list(
    request: Request,
    room_id: str,
    page: int = 1,
    size: int = 50,
    account_details=Depends(is_authenticated_user),
):
    collection_name = "chat_room"
    db = request.app.db

    _db_parser = DBParsers(db, collection_name=collection_name)

    # Create a unique Redis cache key for the room_id, page, and size
    cache_key = f"chat_list:{room_id}:page:{page}:size:{size}"
    redis_instance = await Redis.query_key(key=cache_key)

    try:
        # update the messages unseen to seen.
        # db['chat_room'].find({})

        if redis_instance is None:
            serialized_user_info_result = await _db_parser.get_user_info_result(
                room_id=room_id, page=page, size=size
            )
            await Redis.insert_val(
                key=cache_key, value=json.dumps(serialized_user_info_result)
            )

        else:
            serialized_user_info_result = json.loads(redis_instance)

        payload = get_payload(
            message="User Messages.", ok=True, details=serialized_user_info_result
        )
        return JSONResponse(content=payload, status_code=status.HTTP_200_OK)

    except Exception as e:
        # print("Error: ", e)
        payload = get_payload(message="An un-expected error Occurse.")
        return JSONResponse(
            content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

