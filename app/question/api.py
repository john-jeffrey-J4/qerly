from fastapi import APIRouter, Depends,Request,Response,status,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, join,desc, or_,text
from . import crud

from datetime import datetime
import logging
import os
import json
from fastapi import Query
from typing import Optional
from starlette.responses import JSONResponse

quest_router = APIRouter()


# class UserAnswerRequest(BaseModel):
#     user_id: int
#     pair_id: str

# @quest_router.post("/user_answer/")
# async def save_user_answer(user_answer_request: UserAnswerRequest):
#     user_id = user_answer_request.user_id
#     pair_id = user_answer_request.pair_id

#     # Mocking the answer_json and sort_order for illustration purposes
#     answer_json = {"key": "value"}
#     sort_order = 1

#     db_user_answer = UserAnswer(user_id=user_id, pair_id=pair_id, answer_json=answer_json, sort_order=sort_order)
#     db = SessionLocal()
#     db.add(db_user_answer)
#     db.commit()
#     db.refresh(db_user_answer)
#     db.close()

#     return {"message": "User answer saved successfully", "user_answer": db_user_answer.dict()}