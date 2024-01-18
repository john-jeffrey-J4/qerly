from fastapi import FastAPI
from app.question.api import quest_router
from app.user.api import user_router

app = FastAPI()
app.include_router(quest_router, prefix="/question",
                   tags=["answer"])

app.include_router(user_router, tags=["user_router"])
