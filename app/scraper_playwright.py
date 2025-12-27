from playwright.async_api import async_playwright
from .parser import HTMLParser
from .models import ScrapeResult, ScrapeError

async def fetch_dynamic(url: str, result: ScrapeResult) -> bool:
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # -------- Hacker News pagination --------
            if "news.ycombinator.com" in url:
                pages_html = []

                for pno in range(1, 4):
                    page_url = f"{url}?p={pno}" if pno > 1 else url
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                    result.interactions.pages.append(page_url)
                    pages_html.append(await page.content())

                full_html = "\n".join(pages_html)

                parser = HTMLParser(full_html, url)
                meta, sections = parser.parse()

                result.meta.update(meta)
                result.sections = sections
                result.interactions.scrolls = 0
                result.interactions.clicks.append("pagination:?p=2,3")

                return True

            # -------- Generic JS pages --------
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            result.interactions.pages.append(page.url)

            await _click(page, result)
            await _scroll(page, result)

            html = await page.content()
            parser = HTMLParser(html, page.url)
            meta, sections = parser.parse()

            result.meta.update(meta)
            result.sections = sections

            return True

    except Exception as e:
        result.errors.append(
            ScrapeError(message=str(e), phase="render")
        )
        return False

    finally:
        if browser:
            await browser.close()

async def _click(page, result):
    selectors = [
        "button:has-text('Load more')",
        "button:has-text('Show more')",
        "[role='tab']"
    ]

    for sel in selectors:
        els = await page.query_selector_all(sel)
        for el in els[:2]:
            try:
                await el.click()
                result.interactions.clicks.append(sel)
                await page.wait_for_timeout(800)
                return
            except:
                pass

    result.interactions.clicks.append("no-clickable-elements-found")

async def _scroll(page, result):
    for i in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        result.interactions.scrolls += 1
        result.interactions.pages.append(f"{page.url}?scroll={i+1}")
        await page.wait_for_timeout(1500)
