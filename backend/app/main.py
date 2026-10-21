from fastapi import FastAPI

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.organisations import router as organisations_router
from app.api.research import router as research_router
from app.api.intelligence import router as intelligence_router
from app.api.questions import router as questions_router
from app.api.web_research import router as web_research_router
from app.api.semantic_retrieval import router as semantic_retrieval_router

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI Transformation Strategy Intelligence "
        "platform for FinNova."
    ),
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(organisations_router)
app.include_router(research_router)
app.include_router(intelligence_router)
app.include_router(questions_router)
app.include_router(web_research_router)
app.include_router(semantic_retrieval_router)

@app.get("/")
def root():
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }