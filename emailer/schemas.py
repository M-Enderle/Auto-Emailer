from pydantic import BaseModel, EmailStr


class SendMailRequest(BaseModel):
    html_body: str
    betreff: str
    recipient: EmailStr
    from_address: str | None = None


class BulkJobRequest(BaseModel):
    html_body: str
    betreff: str
    from_address: str | None = None
    batch_size: int
    interval_minutes: int
    file_id: str


