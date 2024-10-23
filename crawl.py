from __future__ import annotations

import asyncio
import httpx

from typing import Callable, Iterable

from utils.urls_utils import UrlParser
from db.crawler_db_actions import store_response_data


class WebCrawler:
    def __init__(
            self,
            client: httpx.AsyncClient,                       # HTTP client
            urls_list: Iterable[str],                        # URLs to start crawling
            filter_url: Callable[[str, str], str | None],    # A list of domains to restrict crawling
            workers: int = 5,                                # Number of concurrent workers
            max_depth: int = 25,                             # Maximum number of links to crawl
    ):
        self.client = client

        self.start_urls = set(urls_list)
        self.work_todo = asyncio.Queue()                      # Queue of URLs to crawl 
        self.urls_seen = set()                                # URLs seen to avoid duplicates
        self.urls_done = set()                                # URLs already crawled

        self.filter_url = filter_url
        self.num_workers = workers
        self.limit = max_depth
        self.total = 0

    async def run(self):
        await self.on_found_links(self.start_urls)
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
        ]
        await self.work_todo.join()

        for worker in workers:
            worker.cancel()

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def process_one(self):
        url = await self.work_todo.get()
        try:
            await self.crawl(url)
        except Exception as exc:
            pass
        finally:
            self.work_todo.task_done()

    async def crawl(self, url: str):

        await asyncio.sleep(.1)

        response = await self.client.get(url, follow_redirects=True)
        
        found_links, page_title = await self.parse_links(
            base=str(response.url),
            text=response.text,
        )

        # Store url, status, content size and page title
        await store_response_data(url, response.status_code, len(response.content), page_title)

        await self.on_found_links(found_links)

        self.urls_done.add(url)

    async def parse_links(self, base: str, text: str) -> set[str]:
        parser = UrlParser(base, self.filter_url)
        parser.feed(text)
        return parser.found_links, parser.page_title

    async def on_found_links(self, urls: set[str]):
        new = urls - self.urls_seen
        self.urls_seen.update(new)
        for url in new:
            await self.put_todo(url)

    async def put_todo(self, url: str):
        if self.total >= self.limit:
            return
        self.total += 1
        await self.work_todo.put(url)
