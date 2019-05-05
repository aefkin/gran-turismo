"""
drivers.py - where the crawling logic lives.

Heavily inspired by following article:
http://www.aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html
"""
from asyncio import Queue, Task
from urllib.parse import urlparse, urljoin
import logging
import re

from lxml import html as lh
from bloom_filter import BloomFilter
import aiohttp


logger = logging.getLogger("races.driver.asyncdriver")


STATIC_REGEX = re.compile('\.(jpg|jpeg|png|svg)', re.IGNORECASE)


DRIVER_VERSION = '1.0'


USER_AGENT = (f'Mozilla/5.0 (compatible; GranTurismoRacingDriver/'
              '{DRIVER_VERSION}; by efkin with <3')


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
        self.root_url = root_url
        self.max_engines = max_engines
        self.max_redirects = max_redirects

        self.q = Queue()
        self.seen_urls = BloomFilter(
            max_elements=expected_urls, error_rate=error_rate)

        # Set authorship in requests
        headers = {"User-Agent": USER_AGENT}

        self.session = aiohttp.ClientSession(headers=headers)

        # Initialize error counters
        self.fives = 0
        self.fours = 0
        self.threes = 0
        self.twos = 0

        # Initialize progress counters
        self.remaining = 0
        self.crawled = 0

        # Initialize results
        self.results = []

    async def drive(self):
        """
        Start the engines until all work is done.
        """
        # Populate the queue.
        await self.q.put((self.root_url, self.max_redirects))
        self.remaining +=1

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
                # Update counters
                self.remaining -= 1

                # check whether is redirecting or not
                if response.status == 301 or response.status == 302:
                    self.threes += 1

                    if max_redirects > 0:
                        next_url = response.headers['location']
                        if next_url in self.seen_urls:
                            # We have been down this path before.
                            return

                        # Remember we have seen this URL.
                        self.seen_urls.add(next_url)

                        # Follow the redirect. One less redirect remains.
                        self.q.put_nowait((next_url, max_redirects - 1))
                elif response.status >= 400:
                    if response.status < 500:
                        self.fours += 1
                        return
                    if 500 <= response.status < 600:
                        self.fives += 1
                        return
                else:
                    self.twos += 1
                    # Parse links from response
                    html = await self.parse_response(response)
                    links = self.parse_links(html)
                    # Bloom-filter logic:
                    for link in links:
                        if link not in self.seen_urls:
                            self.q.put_nowait((link, self.max_redirects))
                            self.seen_urls.add(link)
                            self.remaining += 1

        except Exception as e:
            logger.warning("Exception: {}".format(e))
        finally:
            # Update results.
            self.results.append((url, response.status))
            # Update counters.
            self.crawled += 1
            # Log everything.
            partial_total = self.crawled + self.remaining
            logger.warning(f"Race progress:\t{self.crawled} URLs Crawled"
                           f"\t{self.remaining} URLs Remaining"
                           f"\t{partial_total} Total URLs")

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
        # Gather all links that does not contain hashtags
        xpath_query = "//a[not(contains(@href, '#'))]/@href"
        for href in dom.xpath(xpath_query):
            link = urljoin(self.root_url, href)
            # Skipping static links.
            if STATIC_REGEX.search(link):
                continue
            # Add new links to results
            if link not in self.seen_urls and link.startswith(self.root_url):
                found_links.add(link)
        return found_links
