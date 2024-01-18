from fastapi import APIRouter, Depends, Request, Response, openapi, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, join, desc, or_, text
from . import crud
from app.database import get_db
from datetime import datetime
import logging
import os
import json
from reportlab.pdfgen import canvas

from fastapi import Query
from typing import Optional
from starlette.responses import JSONResponse
from app.question import models, crud, schemas
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI, OpenAIError
import shutil


from fastapi.responses import StreamingResponse  # Import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO 
import textwrap
quest_router = APIRouter()


@quest_router.post("/user_answer/")
async def save_user_answer(user_answer_request: schemas.UserAnswerRequest, db=Depends(get_db)):
    user_id = user_answer_request.user_id
    pair_id = user_answer_request.pair_id
    sort_order = user_answer_request.sort_order
    answer_json = user_answer_request.answer_json
    answer_json_dict = answer_json.dict()
    # Check if the entry already exists
    existing_user_answer = db.query(models.UserAnswer).filter(
        models.UserAnswer.user_id == user_id,
        models.UserAnswer.pair_id == pair_id
    ).first()

    if existing_user_answer:
        # Entry already exists, you can choose to update it or raise an error
        raise HTTPException(
            status_code=400, detail="User answer for this pair_id and user_id already exists")

    db_user_answer = models.UserAnswer(
        user_id=user_id, pair_id=pair_id, answer_json=answer_json_dict, sort_order=sort_order)
    db.add(db_user_answer)
    db.commit()
    db.refresh(db_user_answer)
    db.close()

    return {"message": "User answer saved successfully"}


@quest_router.post("/ranking_response/")
def generatearticle(answer_json_dict: schemas.Ranking):
    """
    Generates an article based on the given prompt.

    Args:
        prompt (str): The prompt for generating the article.

    Returns:
        dict: A dictionary containing the generated article as the value for the "message" key.
    """
    print(answer_json_dict)
    try:
        prompt = "Given the user's answers - Ranking:acceptance, Importance:critical, Performance: Not good - provide a response."
        
        client = OpenAI(api_key="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")
        response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt}
                    ]
                )
        print(response, "res")
        content = response.choices[0].message.content

        return {"message": content}

    except OpenAIError as e:

        # print(e.error)
        raise e
    except HTTPException as e:
    # Handle specific FastAPI HTTP exceptions if needed
        raise e
    # except Exception as e:
    #     # Handle other exceptions (e.g., OpenAIError)
    #     print(e)
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
def draw_wrapped_text(pdf, text, x, y, width, font_size=8, leading=14, words_per_line=14):
    pdf.setFont("Helvetica", font_size)
    pdf.setFillColorRGB(0, 0, 0)

    words = text.split()
    lines = [" ".join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]

    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
        

@quest_router.post("/generate_pdf")
async def generate_pdf(feedback: schemas.UserFeedback):
    try:
        # Create a PDF buffer
        pdf_buffer = BytesIO()

        # Define the page size (letter size)
        width, height = letter

        # Create a PDF document
        pdf = canvas.Canvas(pdf_buffer, pagesize=(width, height))

        # Write content to PDF
        pdf.drawString(100, 800, f"User: {feedback.user['name']}")
        pdf.drawString(100, 780, f"App Name: {feedback.user['app_name']}")

        y_position = 750
        for result in feedback.questionnaire_results:
            pdf.drawString(100, y_position, f"Skill: {result['skill']}")

            # Word wrap for suggestion
            suggestion_text = f"Suggestion: {result['suggestion']}"
            draw_wrapped_text(pdf, suggestion_text, 120, y_position - 20, width=400, words_per_line=12)

            # Word wrap for quote
            quote_text = f"Quote: {result['quote']}"
            draw_wrapped_text(pdf, quote_text, 120, y_position - 80, width=400, font_size=10, leading=12, words_per_line=12)

            y_position -= 120

            if y_position < 50:
                pdf.showPage()  # Start a new page
                y_position = 750  # Reset y-coordinate for the new page

        # Word wrap for closing message
        closing_text = f"Closing Message: {feedback.closing_message}"
        draw_wrapped_text(pdf, closing_text, 100, y_position, width=400, words_per_line=12)

        # Word wrap for team message
        team_text = f"Team Message: {feedback.team_message}"
        draw_wrapped_text(pdf, team_text, 100, y_position - 40, width=400, words_per_line=12)

        # Save the PDF to the buffer
        pdf.save()

        # Move the buffer's cursor to the beginning
        pdf_buffer.seek(0)

        # Specify the folder where you want to save the PDF
        folder_path = "pdf"  # Update this path

        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Save the PDF to a file in the specified folder
        pdf_filename = os.path.join(folder_path, feedback.user['name']+".pdf")
        with open(pdf_filename, "wb") as pdf_file:
            shutil.copyfileobj(pdf_buffer, pdf_file)

        # Return the PDF as a StreamingResponse
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={'Content-Disposition': 'attachment; filename=user_feedback.pdf'})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")