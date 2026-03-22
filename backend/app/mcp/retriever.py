
from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional

from duckduckgo_search import DDGS

from app.mcp.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        max_articles: int = 5,
        min_articles: int = 3,
    ) -> None:
        """Initialize retriever with vector store dependency."""
        self.vector_store = vector_store or VectorStore()
        self.max_articles = max(1, max_articles)
        self.min_articles = min_articles

    @staticmethod
    def _extract_article_content(url: str) -> str:
        """Synchronously download and parse an article with newspaper3k."""
        try:
            from newspaper import Article
        except ImportError as exc:
            raise RuntimeError(
                "Article parsing dependencies are unavailable. Install newspaper3k extras, "
                "including lxml_html_clean, to enable retrieval."
            ) from exc

        article = Article(url)
        article.download()
        article.parse()

        text = (article.text or "").strip()
        if not text:
            raise ValueError("Empty article text")

        return text

    async def _fetch_article_content(self, url: str) -> str:
        """Run the synchronous article extractor in a threadpool."""
        return await asyncio.to_thread(self._extract_article_content, url)

    async def fetch_and_store(self, topic: str) -> List[Dict]:
        """Search the web for topic snippets, extract text, and store in vector DB."""
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("topic must be a non-empty string")

        def _search_ddg(query: str, max_results: int):
            """Synchronous DuckDuckGo search wrapper."""
            results = []
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))
            except Exception as e:
                logging.warning("DDG search failed: %s", e)
            return results

        results = await asyncio.to_thread(_search_ddg, topic, self.max_articles)
        if not results:
            logging.warning("DDG returned no search results for topic: %s", topic)
            return []

        urls = [item.get("href") for item in results if item.get("href")]
        urls = urls[: self.max_articles]

        articles: List[str] = []
        metadatas: List[Dict] = []
        stored_urls: List[str] = []

        for url in urls:
            try:
                content = await self._fetch_article_content(url)
                articles.append(content)
                metadatas.append({"source": url})
                stored_urls.append(url)

                if len(articles) >= self.max_articles:
                    break
            except Exception as exc:
                logging.warning("Failed to fetch or parse %s: %s", url, exc)

        if len(articles) < self.min_articles:
            logging.warning(
                "Only %d articles were fetched for topic '%s'; expected at least %d",
                len(articles),
                topic,
                self.min_articles,
            )

        if not articles:
            return []

        self.vector_store.add_documents(articles, metadatas)

        return [{"source": u, "stored": True} for u in stored_urls]

    def get_context(self, query: str) -> str:
        """Query vector store and return a lightweight summary context."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        results = self.vector_store.query(query, n_results=3)
        if not results:
            return ""

        snippets = [item.get("document", "") for item in results if item.get("document")]
        joined = "\n\n".join(snippets)

        # Optional lightweight summarization strategy (truncate to avoid large payloads).
        max_length = 1500
        if len(joined) <= max_length:
            return joined

        return joined[:max_length].rsplit(" ", 1)[0] + "..."
