from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from functools import wraps
from library.web_scraper import download_cases, upload_to_objectstore, init, current_status

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/pacific/hello")
async def hello():
    return "hiEEEEEEEE"

@app.get("/pacific/status")
async def status():
    return current_status()

@app.get("/pacific/sync")
async def sync():
    return upload_to_objectstore()

@app.get("/pacific/download")
async def download(filters):
    json_convert = json.loads(filters)
    init(json_convert)
    return download_cases()

