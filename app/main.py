from fastapi import FastAPI

from app.api.routes.files import router as files_router

app = FastAPI(
    title="Document Processing API",
    description="An API for processing documents and tabular data.",
    version="0.1.0",
)

app.include_router(files_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
