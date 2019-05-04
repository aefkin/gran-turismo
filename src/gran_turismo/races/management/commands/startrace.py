from datetime import datetime
import asyncio
import logging

from django.core.management.base import BaseCommand

from races import drivers


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start a crawling race"

    def add_arguments(self, parser):
        # Driver options
        parser.add_argument('root_url', help='Starting point')
        parser.add_argument(
            '--max_redirects',
            default=10,
            help='Max number of redirects to follow. Defaults to 10')
        parser.add_argument(
            '--max_engines',
            default=10,
            help='Max number of crawling engines to start. Defaults to 10')
        # Bloom filter options
        parser.add_argument(
            '--bf_expected_urls',
            default=1000,
            help='Bloom filter option. Expected number of ' 
                 'URLs in the bloom filter. Defaults to 1000')
        parser.add_argument(
            '--bf_error_rate',
            default=0.001,
            help='Bloom filter option. Desired error rate '
                 'in false positives. Defaults to 0.001')

    def handle(self, *args, **options):
        # Prepare logging
        root_logger = logging.getLogger("races.startrace")
        if int(options['verbosity']) > 1:
            root_logger.setLevel(logging.DEBUG)

        start = datetime.now()
        logger.warning("Starting at: {}".format(start))

        # Start the race
        logger.warning("Starting event loop...")
        loop = asyncio.get_event_loop()
        logger.warning("Calling the driver...")
        driver = drivers.AsyncDriver(
            root_url=options['root_url'],
            expected_urls=options['bf_expected_urls'],
            error_rate=options['bf_error_rate'],
            max_redirects=options['max_redirects'],
            max_engines=options['max_engines'],
        )
        logger.warning("3...2...1...GO!!!")
        loop.run_until_complete(driver.drive())
        logger.warning("Race ended!")
        end = datetime.now()
        logger.warning("Ending at: {}".format(end))
        loop.close()

        twos = driver.twos
        threes = driver.threes
        fours = driver.fours
        fives = driver.fives

        logger.warning("Elapsed time: {}".format((end-start)))
        logger.warning(f"Found {twos} 2xx")
        logger.warning(f"Found {threes} 3xx")
        logger.warning(f"Found {fours} 4xx")
        logger.warning(f"Found {fives} 5xx")
