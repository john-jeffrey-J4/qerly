from fastapi import FastAPI
from app.question.api import quest_router
app = FastAPI()
app.include_router(quest_router, prefix="/question",
                   tags=["answer"])

@app.get("/")
async def root():
    return {"message": "Hello World"}