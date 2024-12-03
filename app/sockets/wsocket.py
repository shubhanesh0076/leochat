from fastapi import WebSocket, WebSocketDisconnect, Depends
from schemas.chat import MessageModel
from sockets import connection_manager
from api.dependencies import is_authenticated_user_websocket
# from sockets import chat_manager


active_connections: dict[str, set] = dict()

async def chat_websocket_endpoint(
    websocket: WebSocket,
    room_id: str=None,
    current_user=Depends(is_authenticated_user_websocket)
):
    """
    current_user: schemas.User = Depends(get_current_active_user)
    we can't use it because get_current_active_user depends on oauth2_scheme
    which is an instance of OAuth2PasswordBearer.

    OAuth2PasswordBearer does require a Request argument to 
    extract the token from the request. However, when working with 
    WebSocket connections, we won't have access to the request object 
    in the same way you do with HTTP requests.

    so we have to use another technique to retrieve 
    current_user more specifically access-token.

    Thats why we created a TokenManager to reuse it in http request
    as well as in websocket
    """

    await connection_manager.connect(room_id=room_id, websocket=websocket)
    # print(f"WebSocket connection established for chat id: .{room_id}")

    try:
        while True:
            message = await connection_manager.ws_receive_text(websocket)  
            message_info = MessageModel.model_validate_json(message).model_dump()
            message_info["sent_by"]=current_user["user_id"]
            message_info["sent_to"]=None
            # await chat_manager.create_message(data)
            print("DATA: ", message_info)

            # # in serialized_message date time is converted to string
            # serialized_message = {"message": message}
            # message_serializer(new_message.model_dump())
            # print('message_response', serialized_message)

            # Broadcast the message to all connected clients
            # for client_ws in connected_clients[chat_id]:
            #     print('client_ws', client_ws)
            #     await client_ws.send_json(serialized_message)

    except WebSocketDisconnect:
        print("WebSocket connection closed.")
        await connection_manager.disconnect(room_id)
    
    except Exception as e:
        print(f"Error****************: {e}")
        await websocket.close(code=1003)

    # finally:
    #     # Remove disconnected client from the set
    #     print(
    #         f'Removed disconnected client websocket: {websocket} from the Chat id: {room_id}')
    #     # handle removing clients
    #     connected_clients[room_id].remove(websocket)

    #     # handle removing chat_id from connected_clients if no clints are connected
    #     if len(connected_clients[room_id]) == 0:
    #         del connected_clients[room_id]
    #         print(f'Removed chat id: {room_id} as there are no clints.')
    #     print('Finally remaining clints:', connected_clients)