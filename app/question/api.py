from fastapi import APIRouter, Depends, Request, Response, openapi, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, join, desc, or_, text
from . import crud
from app.database import get_db
from datetime import datetime
import logging
import os
import json

from fastapi import Query
from typing import Optional
from starlette.responses import JSONResponse
from app.question import models, crud, schemas
from fastapi import FastAPI, HTTPException

from openai import OpenAI, OpenAIError

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
    # try:
    prompt = f"Given the user's answers - Ranking:acceptance, Importance:critical, Performance: Not good - provide a response."
    # api_key = os.getenv("OPENAI_API_KEY")
    # client = OpenAI(api_key=api_key)
    client = OpenAI(
        api_key="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")
    response = client.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            # {"role": "user", "content": "Where was it played?"}
        ],
        max_tokens=150
    )
    print(response, "res")
    content = response.choices[0].message.content

    return {"message": content}

    # except OpenAIError as e:

    #     print(e.error)
    #     return jsonify(e)
    # except HTTPException as e:
    # # Handle specific FastAPI HTTP exceptions if needed
    #     raise e
    # except Exception as e:
    #     # Handle other exceptions (e.g., OpenAIError)
    #     print(e)
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
