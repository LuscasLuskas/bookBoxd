import requests
from fastapi import HTTPException, status

from app.schemas.book import ExternalBookResult

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_BASE_URL = "https://openlibrary.org"
COVER_URL_TEMPLATE = "https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
SEARCH_FIELDS = "key,title,author_name,first_publish_year,cover_i,isbn"


class OpenLibraryService:
    """Reads book metadata from the public Open Library API.

    Kept separate from BookService so the same mapping can be reused by the
    future bulk import of the Open Library dump.
    """

    def search(self, query: str, limit: int = 20) -> list[ExternalBookResult]:
        try:
            response = requests.get(
                OPEN_LIBRARY_SEARCH_URL,
                params={"q": query, "limit": limit, "fields": SEARCH_FIELDS},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível consultar a Open Library",
            )

        results: list[ExternalBookResult] = []
        for doc in response.json().get("docs", []):
            key = doc.get("key")
            title = doc.get("title")
            if not key or not title:
                continue
            authors = doc.get("author_name") or []
            isbns = doc.get("isbn") or []
            cover_id = doc.get("cover_i")
            results.append(
                ExternalBookResult(
                    external_id=key,
                    title=title[:500],
                    author=(", ".join(authors)[:255] if authors else "Unknown"),
                    cover_url=(
                        COVER_URL_TEMPLATE.format(cover_id=cover_id) if cover_id else None
                    ),
                    published_year=doc.get("first_publish_year"),
                    isbn=(isbns[0][:20] if isbns else None),
                )
            )
        return results

    def fetch_description(self, work_key: str) -> str | None:
        """Fetches a work's description (the search endpoint omits it)."""
        if not work_key.startswith("/works/"):
            return None
        try:
            response = requests.get(f"{OPEN_LIBRARY_BASE_URL}{work_key}.json", timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None

        description = response.json().get("description")
        if isinstance(description, dict):
            description = description.get("value")
        return description if isinstance(description, str) else None
