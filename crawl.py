from __future__ import annotations

import asyncio
import httpx

from typing import Callable, Iterable

from utils.urls_utils import UrlParser
from db.crawler_db_actions import store_data_responses, store_statistics


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
        self.total_number_errors = 0                          # Total number of errors encountered during crawling
        self.total_number_urls_crawled_per_domain = {}        # Total number of URLs crawled per domain
        self.total_number_urls_per_status_code = {}           # Total number of URLs crawled per status code

    async def run(self):
        await self.on_found_links(self.start_urls)
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
        ]
        await self.work_todo.join()

        for worker in workers:
            worker.cancel()
        
        await store_statistics(
            len(self.urls_done), 
            self.total_number_errors, 
            self.total_number_urls_crawled_per_domain,
            self.total_number_urls_per_status_code)
        

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
            self.total_number_errors += 1
            print(f"Error: {exc} for {url}")
        finally:
            self.work_todo.task_done()

    async def crawl(self, url: str):

        await asyncio.sleep(.1)

        response = await self.client.get(url, follow_redirects=True)
        
        self.parser = await self.parse_links(
            base=str(response.url),
            text=response.text,
        )

        # Store url, status, content size and page title
        await store_data_responses(url, response.status_code, len(response.content), self.parser.page_title)

        await self.on_found_links(self.parser.found_links)

        self.urls_done.add(url)

    async def parse_links(self, base: str, text: str) -> set[str]:
        parser = UrlParser(base, self.filter_url, self.total_number_urls_crawled_per_domain)
        parser.feed(text)
        return parser

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
