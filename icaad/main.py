from fastapi import FastAPI

from scripts.web_scraper import download_cases, upload_to_objectstore, init

app = FastAPI()
init()

@app.get("/sync")
async def sync():
    return upload_to_objectstore()

@app.get("/download")
async def download():
    return download_cases()

