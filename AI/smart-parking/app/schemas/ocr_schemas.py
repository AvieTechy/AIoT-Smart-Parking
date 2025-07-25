from pydantic import BaseModel, Field

## OCR Response Schema
class OCRResponse(BaseModel):
    status: bool
    plate: str
