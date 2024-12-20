from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from functools import wraps
from library.web_scraper import download_cases, upload_to_objectstore, init, current_status

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/hello")
async def hello():
    return "hiEEEEEEEE"

@app.get("/status")
async def status():
    return current_status()

@app.get("/sync")
async def sync():
    return upload_to_objectstore()

@app.get("/download")
async def download():
    init()
    return download_cases()

