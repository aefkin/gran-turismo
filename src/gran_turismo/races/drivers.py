"""
drivers.py - where the crawling logic lives.

Heavily inspired by following article:
http://www.aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html
"""
from asyncio import Queue, Task
from urllib.parse import urlparse, urljoin
import logging

from lxml import html as lh
from bloom_filter import BloomFilter
import aiohttp


logger = logging.getLogger("races.driver.asyncdriver")


class AsyncDriver:
    """
    A crawling driver built on top asyncio library. Uses bloom filters for
    URL deduplication. 

    Init Attributes:
        root_url        Starting point for the driver. Expects URL string.
        expected_urls   Maximum capacity of the bloom filter.  
        error_rate      Expected error rate in false positives of the 
                        bloom filter.
        max_redirects   Maximum number of redirects that the driver is
                        following.
        max_engines     Concurrency level.
    """
    def __init__(
            self, root_url, expected_urls,
            error_rate, max_redirects, max_engines,
    ):
        self.max_engines = max_engines
        self.max_redirects = max_redirects
        self.q = Queue()
        self.seen_urls = BloomFilter(
            max_elements=expected_urls, error_rate=error_rate)
        self.root_url = root_url
        self.session = aiohttp.ClientSession()

    async def drive(self):
        """
        Start the engines until all work is done.
        """
        # Populate the queue.
        await self.q.put((self.root_url, self.max_redirects))

        # Start driving.
        engines = [Task(self.start_track())
                  for _ in range(self.max_engines)]

        # When all work is done, exit.
        await self.q.join()
        for engine in engines:
            engine.cancel()
        await self.session.close()

    async def start_track(self):
        """
        Definition of a single worker.
        """
        while True:
            # Gather next link from the queue.
            url, max_redirects = await self.q.get()

            logger.warning(
                "Next URL: {}, remaining redirects {}".format(
                    url, max_redirects
                )
            )

            # Download page and add new links to the queue.
            await self.fetch(url, max_redirects)
            self.q.task_done()

    async def fetch(self, url, max_redirects):
        """
        Fetch a link and add new links to the queue. Eventually 
        follows redirects as needed.
        """
        try:
            async with self.session.get(
                    url,
                    allow_redirects=False, # Handle redirects ourselves.
                    timeout=20) as response:
                # check whether is redirecting or not
                if response.status == 301 or response.status == 302:
                    logger.warning("New redirect found!")
                    if max_redirects > 0:
                        next_url = response.headers['location']
                        logger.warning("New location: {}".format(next_url))
                        if next_url in self.seen_urls:
                            # We have been down this path before.
                            logger.warning("Already been here!")
                            return

                        # Remember we have seen this URL.
                        self.seen_urls.add(next_url)

                        # Follow the redirect. One less redirect remains.
                        self.q.put_nowait((next_url, max_redirects - 1))
                else:
                    # Parse links from response
                    html = await self.parse_response(response)
                    links = self.parse_links(html)
                    # Bloom-filter logic:
                    for link in links:
                        if link not in self.seen_urls:
                            logger.warning("New link found: {}".format(link))
                            self.q.put_nowait((link, self.max_redirects))
                            self.seen_urls.add(link)

        except Exception as e:
            logger.warning("Exception: {}".format(e))

    async def parse_response(self, resp):
        """
        Collects HTML text from response.
        """
        return await resp.text()

    def parse_links(self, html):
        """
        Collect all non-internal links in HTML DOM. Return those ones
        not present in our bloom filter.
        """
        found_links = set()
        dom = lh.fromstring(html)
        # gather all links that does not contain hashtags
        xpath_query = "//a[not(contains(@href, '#'))]/@href"
        for href in dom.xpath(xpath_query):
            link = urljoin(self.root_url, href)
            if link not in self.seen_urls and link.startswith(self.root_url):
                found_links.add(link)
        return found_links

