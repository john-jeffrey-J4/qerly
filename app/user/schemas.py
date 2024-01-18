
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr


class EmailCreate(BaseModel):
    email: EmailStr
    
    
class EmailSend(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    pdf_file: UploadFile
    
    
class JsonData(BaseModel):
    name: str
    age: int
    city: str