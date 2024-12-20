from fastapi import FastAPI, Request, Query
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

@app.get("/hello")
async def hello():
    return "hiEEEEEEEE"

@app.get("/status")
async def status():
    return current_status()

@app.get("/sync")
async def sync():
    return upload_to_objectstore()


#?countries=[%20"Fiji",%20"Papua%20new%20guinea",%20"Tonga",%20"Samoa"%20]
#curl -X POST "http://127.0.0.1:8000/download" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"test_key\":\"test_val\"}"

@app.get("/download")
async def download(filters):
    json_convert = json.loads(filters)
    init(json_convert)
    return download_cases()

#http://127.0.0.1:8000/download?filters=%20{%22countries%22:%20[%20%22Fiji%22,%20%22Papua%20new%20guinea%22,%20%22Tonga%22,%20%22Samoa%22%20]}