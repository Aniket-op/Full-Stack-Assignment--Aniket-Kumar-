# Lyftr AI Universal Website Scraper

A full-stack website scraper built with **FastAPI**, **Playwright**, and **BeautifulSoup**. It supports static scraping with dynamic fallback for JS-heavy sites, interactions (clicks/scrolls), and noise filtering.

## How to Run

1.  **Prerequisites**: Python 3.10+ installed.
2.  **Run the helper script** (Windows Git Bash / Linux / Mac):
    ```bash
    chmod +x run.sh
    ./run.sh
    ```
    *Note: The script creates a virtual environment, installs requirements, installs Playwright browsers, and starts the server.*

3.  **Access the GUI**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## Environment Details
-   **Scraper**: Uses `httpx` for static and `playwright` (Chromium) for dynamic execution.
-   **Server**: Uvicorn running FastAPI.
-   **Frontend**: Server-rendered Jinja2 template with Vanilla JS for API interaction.

## Tested URLs

1.  **https://en.wikipedia.org/wiki/Artificial_intelligence**
    -   *Type*: Static Page
    -   *Result*: Successfully parsed via Static scraper. Sections are well-defined by headers.
    -   <img width="1257" height="934" alt="image" src="https://github.com/user-attachments/assets/500b476c-7644-40b9-9f53-63aa48148373" />

2.  **https://vercel.com/**
    -   *Type*: JS-heavy Marketing Page
    -   *Result*: Fallback to Playwright triggered. Sections like "Hero", "Features" are extracted. Interactive elements present.
    -   <img width="1264" height="922" alt="image" src="https://github.com/user-attachments/assets/fa6c60b4-711a-4bd1-a2a5-244363749aac" />

3.  **https://news.ycombinator.com/**
    -   *Type*: Pagination / List
    -   *Result*: Scraper captures the list. Note: Pagination interaction might be limited to scrolling in this MVP configuration.
    -   <img width="505" height="753" alt="image" src="https://github.com/user-attachments/assets/e657a6d2-fb78-47c8-8c22-03e5cf332149" />


## Known Limitations
-   **Pagination**: The current interaction logic focuses on "Infinite Scroll" (scrolling to bottom) and "Load More" buttons. It does not explicitly follow "Next Page" links `<a>` in this version, preferring single-page enrichment.
-   **Section Grouping**: Complex nested layouts might result in flattened or generic "Section" types if semantic HTML is significantly lacking.
-   **Performance**: Playwright fallback can take 10-30 seconds depending on the site speed and wait times.
#
