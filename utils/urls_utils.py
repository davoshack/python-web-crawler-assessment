import html.parser
import pathlib
import urllib.parse

from typing import Callable

class UrlFilterer:
    def __init__(
            self,
            domains: set[str] | None = None,
            blacklist: set[str] | None = None,
    ):
        self.domains = domains
        self.blacklist = blacklist

    def filter_url(self, base: str, url: str) -> str | None:
        url = urllib.parse.urljoin(base, url)
        url, _ = urllib.parse.urldefrag(url)
        parsed = urllib.parse.urlparse(url)
        if (self.domains is not None
                and parsed.netloc not in self.domains):
            return None
        ext = pathlib.Path(parsed.path).suffix
        if (self.blacklist is not None
                and ext in self.blacklist):
            return None
        return url


class UrlParser(html.parser.HTMLParser):
    def __init__(
            self,
            base: str,
            filter_url: Callable[[str, str], str | None]
    ):
        super().__init__()
        self.base = base
        self.filter_url = filter_url
        self.found_links = set()
        self.page_title = "Title not found"

    def get_title(self) -> str:
        page_title = self.rawdata.split("<title>")[1].split("</title>")[0] 
        return page_title

    def handle_starttag(self, tag: str, attrs):
        if tag != "a":
            if tag == "title":
                self.page_title = self.get_title()
            else:
                return

        for attr, url in attrs:
            if attr != "href":
                continue

            if (url := self.filter_url(self.base, url)) is not None:
                self.found_links.add(url)