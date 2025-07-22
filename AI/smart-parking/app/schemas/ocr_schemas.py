from pydantic import BaseModel, Field

## OCR Response Schema
class OCRResponse(BaseModel):
    text: str
