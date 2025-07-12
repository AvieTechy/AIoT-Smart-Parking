from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class GateType(str, Enum):
    IN = "In"
    OUT = "Out"

class Session(BaseModel):
    plate_url: str = Field(..., description="URL ảnh biển số (Cloudinary)", alias="plateUrl")
    face_url: str = Field(..., description="URL ảnh khuôn mặt (Cloudinary)", alias="faceUrl")
    timestamp: str = Field(..., description="Timestamp as string")
    gate: str = Field(..., description="In hoặc Out")
    is_out: bool = Field(default=False, description="false khi mới tạo", alias="isOut")
    face_index: str = Field(..., description="Face index", alias="faceIndex")
    plate_number: Optional[str] = Field(None, description="Plate number (null initially)", alias="plateNumber")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class IsNewSession(BaseModel):
    status: bool = Field(..., description="true nếu đang có session mới")
    session_id: str = Field(..., description="session hiện tại", alias="sessionID")

    class Config:
        populate_by_name = True

class MatchingVerify(BaseModel):
    session_id: str = Field(..., description="Session ID của lượt ra", alias="sessionID")
    is_match: bool = Field(..., description="So khớp thành công hay không", alias="isMatch")

    class Config:
        populate_by_name = True

class SessionMap(BaseModel):
    entry_session_id: str = Field(..., description="Session ID lúc vào", alias="entrySessionID")
    exit_session_id: str = Field(..., description="Session ID lúc ra", alias="exitSessionID")

    class Config:
        populate_by_name = True

class PlateMap(BaseModel):
    session_id: str = Field(..., description="ID của session tương ứng")

class ParkingSlot(BaseModel):
    location_code: str = Field(..., description="Ví dụ A1 (tuỳ thiết kế grid hoặc số thứ tự)")
    is_occupied: bool = Field(..., description="true nếu đang có xe, false nếu trống")
    updated_at: datetime = Field(default_factory=datetime.now, description="Lần cập nhật cuối")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Request models for API
class SessionCreateRequest(BaseModel):
    plate_url: str = Field(..., alias="plateUrl")
    face_url: str = Field(..., alias="faceUrl")
    gate: str = Field(..., description="In or Out")
    face_index: str = Field(..., alias="faceIndex")
    plate_number: Optional[str] = Field(None, alias="plateNumber", description="Required for Out sessions, detected for In sessions")

    class Config:
        populate_by_name = True

# Response models for API
class SessionResponse(BaseModel):
    session_id: str
    session: Session

class ParkingSlotResponse(BaseModel):
    slot_id: str
    slot: ParkingSlot

class PlateDetectionRequest(BaseModel):
    session_id: str
    plate_url: str

class SessionUpdateRequest(BaseModel):
    plate_number: Optional[str] = Field(None, alias="plateNumber")

    class Config:
        populate_by_name = True

class FaceMatchingRequest(BaseModel):
    exit_session_id: str
    entry_session_id: str
