from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from app.database import SessionLocal, get_db
from app.user.schemas import EmailCreate, JsonData
from app.user.models import Email
from email.message import EmailMessage
from aiosmtplib import send
from email import encoders
from reportlab.pdfgen import canvas



user_router = APIRouter()


@user_router.post('/save_email')
async def save_email(email_data: EmailCreate, db: SessionLocal = Depends(get_db)):
    # Check if the email already exists in the database
    existing_email = db.query(Email).filter(
        Email.email == email_data.email).first()

    if existing_email:
        return {'success': True, 'message': 'Email already exists', 'id': existing_email.id}

    # Create an instance of the Email model
    new_email = Email(email=email_data.email)

    # Add the new email to the database
    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    return {'success': True, 'message': 'Email saved successfully', 'id': new_email.id}


@user_router.get('/a')
async def g(db: SessionLocal = Depends(get_db)):
    existing_email = db.query(Email).first()
    return existing_email


# FastAPI endpoint to send emails
@user_router.post('/send_mail')
async def send_mail_with_attachment(to_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    pdf_file: UploadFile = File(...)):
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(body))
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_ADDRESS")
    msg['To'] = to_email

    # Attach the PDF file from form data
    pdf_content = await pdf_file.read()
    pdf_part = MIMEBase('application', 'octet-stream')
    pdf_part.set_payload(pdf_content)
    encoders.encode_base64(pdf_part)
    pdf_part.add_header('Content-Disposition', f'attachment; filename={pdf_file.filename}')
    msg.attach(pdf_part)

    try:
        await send(msg,
                   hostname=os.getenv("EMAIL_SMTP_SERVER_HOST"),
                   port=int(os.getenv("SMTP_PORT")),
                   use_tls=False,
                   username=os.getenv("EMAIL_ADDRESS"),
                   password=os.getenv("EMAIL_PASSWORD"),)
        return {'success': True, 'message': 'Email sent successfully'}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send email: {str(e)}")
        
        
        
        


def create_pdf_from_json(json_data):
    output_filename = 'output.pdf'
    
    # Create a PDF canvas
    pdf_canvas = canvas.Canvas(output_filename)

    # Convert JSON data to a string representation
    json_str = json.dumps(json_data.dict(), indent=4)

    # Write the JSON string to the PDF
    pdf_canvas.drawString(100, 700, json_str)

    # Save the PDF
    pdf_canvas.save()

    return output_filename

@user_router.post('/generate_pdf')
async def generate_pdf(json_data: JsonData):
    try:
        pdf_filename = create_pdf_from_json(json_data)
        return FileResponse(pdf_filename, filename='output.pdf', media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
