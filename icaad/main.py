import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sse_starlette import EventSourceResponse
import json
from library.web_scraper import download_cases, upload_to_objectstore, init, whats_on_objectstore, objectstore_stats, report_per_country_local

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/v0/pacific/hello")
async def hello():
    return "hiEEEEEEEE"

@app.get("/v0/pacific/stats")
async def stats(filters,refresh= False):
    json_convert = json.loads(filters)
    init(json_convert,refresh)
    return await objectstore_stats()

@app.get("/v0/pacific/local_stats")
async def local_stats(filters,refresh= False):
    json_convert = json.loads(filters)
    init(json_convert,refresh)
    return await report_per_country_local()
     
@app.get("/v0/pacific/objectstore_log")
async def objectstore_log():
    return EventSourceResponse(whats_on_objectstore())
   
@app.get("/v0/pacific/sync")
async def sync():
    return EventSourceResponse(upload_to_objectstore())

@app.get("/v0/pacific/download")
async def download(filters, refresh= False):
    json_convert = json.loads(filters)
    init(json_convert,refresh)
    return await download_cases()
