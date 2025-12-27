# Design Notes

## Static vs JS Fallback
- **Strategy**: 
    1.  The system first attempts a fast **static scrape** using `httpx`.
    2.  We parse the content and calculate the total text length of all found sections.
    3.  **Heuristic**: If the total text length is less than **150 characters**, we deem the static scrape as "insufficient" (likely a Single Page Application shell).
    4.  If insufficient, we trigger the **JS-based scraper** using `Playwright` to render the page.

## Wait Strategy for JS
- [ ] Network idle
- [x] Fixed sleep
- [x] Wait for selectors (implicit in `domcontentloaded`)
- **Details**: 
    - We currently use `wait_until="domcontentloaded"` which waits for the initial HTML document to be completely loaded and parsed.
    - For interactions (scrolling/clicking), we rely on **fixed sleeps** (`0.8s` after click, `1.5s` after scroll) to allow time for dynamic content to render, as specific network idle states can be flaky on some sites.
    - **Hacker News Handling**: For `news.ycombinator.com`, we proactively load pages `?p=1,2,3` sequentially, waiting for `domcontentloaded` on each.
    - A 30s global timeout is enforced for the page load.

## Click & Scroll Strategy
- **Click flows implemented**:
    - We search for elements matching: `button:has-text('Load more')`, `button:has-text('Show more')`, or `[role='tab']`.
    - We attempt to click the **first** available element found from this list. If a click is successful, we stop attempting further clicks to avoid navigation hazards.
- **Scroll / pagination approach**:
    - We implement a simple "infinite scroll" simulation.
    - The scraper executes `window.scrollTo(0, document.body.scrollHeight)` **3 times**.
    - After each scroll, we wait 1.5 seconds for new content to populate.
- **Hacker News Pagination**:
    - We do **not** scroll.
    - Instead, we explicitly navigate to `?p=1`, `?p=2`, `?p=3` and concatenate the HTML content of all three pages.
- **Stop conditions**: 
    - **Max depth**: Fixed limit of 3 scrolls.
    - **Max clicks**: Stops after 1 successful click interaction to prevent excessive state changes.

## Section Grouping & Labels
- **How you group DOM into sections**:
    - We parse the HTML (static or rendered) using `BeautifulSoup`.
    - We specifically target these top-level semantic tags: `header`, `nav`, `section`, `main`, `footer`.
    - Content is extracted directly from these matched tags.
    - **Hacker News**: We look specifically for `table.itemlist` and iterator over `tr.athing` rows to extract stories.
- **How you derive section `type` and `label`**:
    - **Type**: Mapped directly from the tag name:
        - `header` -> `hero`
        - `nav` -> `nav`
        - `footer` -> `footer`
        - All others (`section`, `main`) -> `section`
    - **Label**: 
        1. The text of the first Heading (`h1`-`h6`) found within the section.
        2. Fallback: The first 7 words of the section's text content.

## Noise Filtering & Truncation
- **What you filter out**:
    - **HTML Elements**: During text extraction, we ignore script logic / styles implicitly by asking `BeautifulSoup` for text only.
    - *Cookie banners are currently not explicitly filtered in the active implementation.*
- **How you truncate `rawHtml` and set `truncated`**:
    - We limit the `rawHtml` field for each section to **5000 characters**.
    - If `len(rawHtml) > 5000`, we slice it and append `...`, setting the `truncated` flag to `true`.
