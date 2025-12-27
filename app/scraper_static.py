import httpx
from .parser import HTMLParser
from .models import ScrapeResult, ScrapeError

async def fetch_static(url: str, result: ScrapeResult) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()

        parser = HTMLParser(r.text, str(r.url))
        meta, sections = parser.parse()

        result.meta.update(meta)
        result.sections = sections

        text_len = sum(len(s.content.text) for s in sections)
        link_count = sum(len(s.content.links) for s in sections)

        if text_len < 150:
            result.errors.append(
                ScrapeError(
                    message="Static content insufficient, fallback to JS",
                    phase="static_check"
                )
            )
            return False

        return True

    except Exception as e:
        result.errors.append(
            ScrapeError(message=str(e), phase="fetch")
        )
        return False
