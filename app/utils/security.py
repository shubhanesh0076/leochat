import fastapi
import hashlib
from fastapi.websockets import WebSocket
from passlib.hash import pbkdf2_sha256
from fastapi.requests import Request
from user_agents import parse  # Install: pip install pyyaml ua-parser user-agents
import uuid


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed_password)


def is_authenticated(user_data: dict, client_credentials: dict) -> bool:
    client_password = client_credentials.get("password", None)
    db_password = user_data.get("password", None)
    is_verified = verify_password(password=client_password, hashed_password=db_password)
    if not is_verified:
        return False
    return True

def generate_hash(info: str) -> str:
    return hashlib.sha256(f"{info}".encode()).hexdigest()

def generate_device_hash_for_validation(user_id: str, device_id: str, random_device_uuid: str):
    """
    This is used for conver into Hash.
    """
    info=f"{user_id}leo{device_id}chat{random_device_uuid}"
    device_hash_key = generate_hash(info)
    return device_hash_key
    
def generate_device_id(request: Request, email: str):
    user_agent = request.headers.get("User-Agent", "Unknown")
    info = f"{email}{user_agent}"
    return generate_hash(info)

def generate_device_id_websocket(websocket: WebSocket, email: str):
    user_agent = websocket.headers.get("X-Device-ID", "Unknown")
    device_id = hashlib.sha256(f"{email}{user_agent}".encode()).hexdigest()
    return device_id

def get_device_info(request: Request) -> dict:
    user_agent_string = request.headers.get("User-Agent", "Unknown")
    user_agent = parse(user_agent_string)

    device_name = (
        f"{user_agent.device.brand or 'Unknown'} {user_agent.device.model or 'Device'}"
    )
    os = user_agent.os.family
    browser = user_agent.browser.family
    is_mobile = user_agent.is_mobile
    is_tablet = user_agent.is_tablet
    is_pc = user_agent.is_pc

    device_type = "Unknown"
    if is_mobile:
        device_type = "Mobile"
    if is_tablet:
        device_type = "Tablet"
    if is_pc:
        device_type = "PC"
    
    device_info = {
        "device_name": device_name,
        "os": os,
        "browser": browser,
        "device_type": device_type,
    }
    return device_info


def combined_device_info(request, email: str) -> dict:
    device_id = generate_device_id(request, email)
    device_info = get_device_info(request)
    device_info["device_id"] = device_id
    device_info["random_device_uuid"]=str(uuid.uuid4())
    return device_info
