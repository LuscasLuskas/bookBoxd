import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


class GoogleBooksClient:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key=None, rate_limit_per_sec=3):
        self.session = requests.Session()
        self.api_key = api_key
        self.rate_limit = rate_limit_per_sec
        self.last_request = 0

    def _throttle(self):
        elapsed = time.time() - self.last_request
        min_interval = 1 / self.rate_limit

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_request = time.time()

    def _get(self, params, retries=5):
        for attempt in range(retries):
            self._throttle()

            resp = self.session.get(self.BASE_URL, params=params)

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                wait = 2 ** attempt
                print(f"[RATE LIMIT] {wait}s")
                time.sleep(wait)
                continue

            resp.raise_for_status()

        raise RuntimeError("Falha na requisição")

    def search(self, query, start_index=0, max_results=40):
        params = {
            "q": query,
            "startIndex": start_index,
            "maxResults": max_results
        }

        if self.api_key:
            params["key"] = self.api_key

        return self._get(params)

    def parse(self, item):
        volume = item.get("volumeInfo", {})

        isbn = None
        for identifier in volume.get("industryIdentifiers", []):
            if "ISBN" in identifier.get("type", ""):
                isbn = identifier.get("identifier")

        return {
            "id": item.get("id"),
            "title": volume.get("title"),
            "author": ", ".join(volume.get("authors", [])) if volume.get("authors") else None,
            "edition": isbn,
            "cover": volume.get("imageLinks", {}).get("thumbnail")
        }


def crawl_google_books(client, queries, pages=5):
    seen = set()
    results = []

    for query in queries:
        print(f"[QUERY] {query}")

        for page in range(pages):
            start = page * 40

            data = client.search(query, start_index=start)
            items = data.get("items", [])

            if not items:
                break

            for item in items:
                book_id = item.get("id")

                if book_id in seen:
                    continue

                seen.add(book_id)

                results.append(client.parse(item))

    return results


if __name__ == "__main__":
    queries = ["Harry Potter e a Pedra Filosofal"]

    client = GoogleBooksClient(api_key=API_KEY)

    books = crawl_google_books(client, queries, pages=3)

    for b in books[:10]:
        print(b)