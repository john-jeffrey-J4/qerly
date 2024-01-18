from fastapi import FastAPI
from app.question.api import quest_router
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}