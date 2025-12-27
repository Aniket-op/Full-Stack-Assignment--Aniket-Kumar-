from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .models import Section, SectionContent
import re

class HTMLParser:
    def __init__(self, html: str, url: str):
        self.soup = BeautifulSoup(html, "html.parser")
        self.url = url

    def parse(self):
        meta = self._meta()

        # 1️⃣ Special handling: Hacker News (table-based layout)
        hn_sections = self._parse_hacker_news()
        if hn_sections:
            return meta, hn_sections

        # 2️⃣ Normal semantic parsing
        sections = self._semantic_sections()

        return meta, sections

    # ---------------- META ----------------

    def _meta(self):
        title = self.soup.title.string if self.soup.title else ""
        desc = self.soup.find("meta", attrs={"name": "description"})
        canon = self.soup.find("link", rel="canonical")

        return {
            "title": title.strip() if title else "",
            "description": desc["content"].strip() if desc else "",
            "language": self.soup.html.get("lang", "en") if self.soup.html else "en",
            "canonical": urljoin(self.url, canon["href"]) if canon else None
        }

    # ---------------- HACKER NEWS ----------------

    def _parse_hacker_news(self):
        itemlist = self.soup.select_one("table.itemlist")
        if not itemlist:
            return None

        links = []
        for row in itemlist.select("tr.athing"):
            a = row.select_one("a.storylink, a.titlelink")
            if a:
                links.append({
                    "text": a.get_text(strip=True),
                    "href": urljoin(self.url, a["href"])
                })

        if not links:
            return None

        content = SectionContent(
            headings=["Top Stories"],
            text="Hacker News front page stories",
            links=links,
            images=[],
            lists=[[l["text"] for l in links]],
            tables=[]
        )

        raw = str(itemlist)
        truncated = len(raw) > 5000
        raw = raw[:5000] + "..." if truncated else raw

        return [
            Section(
                id="list-0",
                type="list",
                label="Top Stories",
                sourceUrl=self.url,
                content=content,
                rawHtml=raw,
                truncated=truncated
            )
        ]

    # ---------------- GENERIC SEMANTIC SECTIONS ----------------

    def _semantic_sections(self):
        sections = []
        idx = 0

        tags = self.soup.find_all(
            ["header", "nav", "section", "main", "footer"]
        )

        for tag in tags:
            text = tag.get_text(" ", strip=True)
            if not text:
                continue

            content = SectionContent(
                headings=[
                    h.get_text(strip=True)
                    for h in tag.find_all(re.compile("^h[1-6]$"))
                ],
                text=text,
                links=[
                    {
                        "text": a.get_text(strip=True),
                        "href": urljoin(self.url, a["href"])
                    }
                    for a in tag.find_all("a", href=True)
                ],
                images=[
                    {
                        "src": urljoin(self.url, img["src"]),
                        "alt": img.get("alt", "")
                    }
                    for img in tag.find_all("img", src=True)
                ],
                lists=[
                    [
                        li.get_text(strip=True)
                        for li in ul.find_all("li")
                    ]
                    for ul in tag.find_all(["ul", "ol"])
                ],
                tables=[]
            )

            raw = str(tag)
            truncated = len(raw) > 5000
            raw = raw[:5000] + "..." if truncated else raw

            label = (
                content.headings[0]
                if content.headings
                else " ".join(text.split()[:7])
            )

            sections.append(
                Section(
                    id=f"{self._map_type(tag)}-{idx}",
                    type=self._map_type(tag),
                    label=label,
                    sourceUrl=self.url,
                    content=content,
                    rawHtml=raw,
                    truncated=truncated
                )
            )
            idx += 1

        return sections

    def _map_type(self, tag):
        if tag.name == "header":
            return "hero"
        if tag.name == "nav":
            return "nav"
        if tag.name == "footer":
            return "footer"
        return "section"
