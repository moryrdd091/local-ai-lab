from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("searxng-search")

SEARXNG_URL = "http://localhost:8080/search"
DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 10


@mcp.tool()
async def search_web(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> list[dict[str, Any]]:
    """Search the public web through local SearXNG. Read-only; returns titles, URLs, and snippets."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    limit = max(1, min(int(max_results), MAX_RESULTS_LIMIT))
    params = {
        "q": query.strip(),
        "format": "json",
        "language": "fr-FR",
        "safesearch": 1,
    }

    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
    ) as client:
        response = await client.get(SEARXNG_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    results = []
    for item in payload.get("results", [])[:limit]:
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "published_date": item.get("publishedDate")
                or item.get("pubdate")
                or "",
            }
        )

    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")
