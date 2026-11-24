import json
import os
import re
import urllib.parse
import urllib.request
from html import unescape
from typing import List, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebSearchToolInput(BaseModel):
    """Input schema for WebSearchTool."""

    query: str = Field(..., description="Search query for recent news and web results.")
    max_results: int = Field(
        6, ge=1, le=10, description="Maximum number of results to return (1-10)."
    )


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for recent information about a topic. "
        "Returns a numbered list of results with title, URL, source/date when available, and snippet. "
        "Use these URLs as citations in research and reports."
    )
    args_schema: Type[BaseModel] = WebSearchToolInput

    def _run(self, query: str, max_results: int = 6) -> str:
        query = (query or "").strip()
        if not query:
            return "No query provided."
        max_results = max(1, min(int(max_results or 6), 10))

        providers = (
            ("tavily", self._search_tavily),
            ("serper", self._search_serper),
            ("duckduckgo", self._search_duckduckgo),
        )
        errors = []
        for name, fn in providers:
            try:
                results = fn(query, max_results)
                if results:
                    return self._format_results(query, name, results)
                errors.append(f"{name}: no results")
            except Exception as e:
                errors.append(f"{name}: {e}")

        if errors:
            return (
                f'No web search results found for "{query}". '
                f"Provider attempts: {'; '.join(errors)}"
            )
        return f'No web search results found for "{query}".'

    def _search_tavily(self, query: str, max_results: int) -> List[dict]:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY not set")
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        data = self._post_json("https://api.tavily.com/search", payload)
        results = []
        for item in data.get("results", []) or []:
            url = item.get("url")
            title = item.get("title") or "Untitled"
            if not url:
                continue
            results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": item.get("content") or "",
                    "date": item.get("published_date") or "",
                    "source": self._source_from_url(url),
                }
            )
        return results[:max_results]

    def _search_serper(self, query: str, max_results: int) -> List[dict]:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise RuntimeError("SERPER_API_KEY not set")
        payload = {"q": query, "num": max_results}
        data = self._post_json(
            "https://google.serper.dev/search",
            payload,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        )
        results = []
        for item in data.get("organic", []) or []:
            url = item.get("link")
            if not url:
                continue
            results.append(
                {
                    "title": item.get("title") or "Untitled",
                    "url": url,
                    "snippet": item.get("snippet") or "",
                    "date": item.get("date") or "",
                    "source": item.get("source") or self._source_from_url(url),
                }
            )
        return results[:max_results]

    def _search_duckduckgo(self, query: str, max_results: int) -> List[dict]:
        url = "https://html.duckduckgo.com/html/"
        body = urllib.parse.urlencode({"q": query}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                ),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        results = []
        # Prefer primary web results.
        blocks = re.findall(r'<a[^>]+class="result__a"[^>]*>.*?</a>.*?</div>', html, re.S | re.I)
        if not blocks:
            blocks = re.findall(r'<a[^>]+class="result__a"[^>]*>.*?(?:<td|</tr>|</div>)', html, re.S | re.I)
        for block in blocks:
            link_match = re.search(r'class="result__a"[^>]*href="([^"]+)"', block, re.I)
            title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.S | re.I)
            snippet_match = re.search(
                r'class="result__snippet"[^>]*>(.*?)</(?:a|div|td)>', block, re.S | re.I
            )
            if not snippet_match:
                snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)<', block, re.S | re.I)
            if not link_match or not title_match:
                continue
            result_url = self._normalize_ddg_url(unescape(link_match.group(1)))
            if not result_url:
                continue
            title = self._clean_html(title_match.group(1))
            snippet = self._clean_html(snippet_match.group(1)) if snippet_match else ""
            results.append(
                {
                    "title": title or "Untitled",
                    "url": result_url,
                    "snippet": snippet,
                    "date": "",
                    "source": self._source_from_url(result_url),
                }
            )
            if len(results) >= max_results:
                break
        return results

    def _post_json(self, url: str, payload: dict, headers: dict | None = None) -> dict:
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=req_headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def _format_results(self, query: str, provider: str, results: List[dict]) -> str:
        lines = [f'Web search results for "{query}" (provider: {provider}):']
        for i, item in enumerate(results, 1):
            title = (item.get("title") or "Untitled").strip()
            url = (item.get("url") or "").strip()
            source = (item.get("source") or self._source_from_url(url)).strip()
            date = (item.get("date") or "").strip()
            snippet = re.sub(r"\s+", " ", (item.get("snippet") or "").strip())
            meta_parts = [p for p in (source, date) if p]
            meta = f" ({', '.join(meta_parts)})" if meta_parts else ""
            lines.append(f"{i}. {title}{meta}")
            if url:
                lines.append(f"   URL: {url}")
            if snippet:
                lines.append(f"   Snippet: {snippet}")
        lines.append(
            "Use the URLs above as citations. When reporting, include a Sources section listing each cited title and URL."
        )
        return "\n".join(lines)

    @staticmethod
    def _normalize_ddg_url(href: str) -> str:
        if not href:
            return ""
        if href.startswith("//"):
            href = "https:" + href
        if "duckduckgo.com/l/?" in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            uddg = qs.get("uddg", [""])[0]
            if uddg:
                return urllib.parse.unquote(uddg)
        return href

    @staticmethod
    def _clean_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text or "")
        return re.sub(r"\s+", " ", unescape(text)).strip()

    @staticmethod
    def _source_from_url(url: str) -> str:
        try:
            host = urllib.parse.urlparse(url).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            return host or ""
        except Exception:
            return ""
