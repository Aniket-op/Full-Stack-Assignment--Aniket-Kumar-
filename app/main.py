from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime
import asyncio, sys

from .models import *
from .scraper_static import fetch_static
from .scraper_playwright import fetch_dynamic

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/healthz", response_model=HealthResponse)
async def healthz():
    return {"status": "ok"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest):
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Only http(s) URLs allowed")

    result = ScrapeResult(
        url=req.url,
        scrapedAt=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        meta={"title": "", "description": "", "language": "", "canonical": None},
        sections=[],
        interactions=Interactions(),
        errors=[]
    )

    success = await fetch_static(req.url, result)
    if not success:
        result.sections = []
        await fetch_dynamic(req.url, result)

    if not result.sections:
        result.sections.append(
            Section(
                id="unknown-0",
                type="unknown",
                label="Main Content",
                sourceUrl=result.url,
                content=SectionContent(
                    text="No structured sections detected. Fallback content."
                ),
                rawHtml="",
                truncated=False
            )
        )



    return ScrapeResponse(result=result)

@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    return templates.TemplateResponse("index.html", {"request": req})
