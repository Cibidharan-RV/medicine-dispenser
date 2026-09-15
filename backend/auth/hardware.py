from fastapi import Header, HTTPException, status
from backend.config import settings

def verify_hardware_api_key(x_hardware_api_key: str = Header(..., description="RFID or Hardware API Key from ESP32")):
    # The ESP32 is expected to read the RFID card and pass it as the X-Hardware-Api-Key header
    # or pass a hardcoded hardware key to authenticate itself.
    if x_hardware_api_key != settings.HARDWARE_API_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Hardware API Key",
        )
    return x_hardware_api_key
