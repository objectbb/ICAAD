from fastapi import FastAPI

from scripts.web_scraper import download_cases, upload_to_objectstore, init

app = FastAPI()


@app.get("/sync")
async def sync():
    return upload_to_objectstore()

@app.get("/download")
async def download():
    init()
    return download_cases()

