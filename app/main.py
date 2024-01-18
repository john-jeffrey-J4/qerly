from fastapi import FastAPI
from app.question.api import quest_router
from app.user.api import user_router
from app.reports.api import report_router

app = FastAPI()
app.include_router(quest_router, prefix="/question",
                   tags=["answer"])

app.include_router(user_router, tags=["user_router"])
app.include_router(report_router, tags=["report_router"])


