from datetime import datetime
import asyncio
import logging

from django.core.management.base import BaseCommand

from races import drivers, models, collector


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Start a crawling race"

    def add_arguments(self, parser):
        # Driver options
        parser.add_argument('root_url', help='Starting point')
        parser.add_argument(
            '--max_redirects',
            type=int,
            default=10,
            help='Max number of redirects to follow. Defaults to 10')
        parser.add_argument(
            '--max_engines',
            type=int,
            default=10,
            help='Max number of crawling engines to start. Defaults to 10')
        # Bloom filter options
        parser.add_argument(
            '--bf_expected_urls',
            type=int,
            default=1000,
            help='Bloom filter option. Expected number of ' 
                 'URLs in the bloom filter. Defaults to 1000')
        parser.add_argument(
            '--bf_error_rate',
            type=int,
            default=0.001,
            help='Bloom filter option. Desired error rate '
                 'in false positives. Defaults to 0.001')
        parser.add_argument(
            '--limit',
            type=int,
            default=500000,
            help='Limit number of crawled URLs. Defaults to 500000')
        parser.add_argument(
            '--collect-all',
            action='store_true',
            default=False,
            help='By default GT only stores 4xx and 5xx URLs. Enabling '
                 'this flag it would also collect other URLs')

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
            limit=options['limit'],
            collect_all=options['collect_all'],
        )
        logger.warning("3...2...1...GO!!!")
        loop.run_until_complete(driver.drive())

        # Race completed
        logger.warning("Race ended!")
        loop.close()
        end = datetime.now()
        logger.warning("Ending at: {}".format(end))

        # Store session
        session = models.RacingSession.objects.create(
            base_url=options["root_url"],
            starting_time=start,
            ending_time=end,
            successes=driver.twos,
            redirects=driver.threes,
            soft_errors=driver.fours,
            hard_errors=driver.fives,
            crawled=driver.crawled,
        )
        # Store results
        collector.Collector(session.id, driver.results).collect()

        # Some extra stats
        logger.warning("Elapsed time: {}".format((end-start)))
        logger.warning(f"Found {driver.twos} 2xx")
        logger.warning(f"Found {driver.threes} 3xx")
        logger.warning(f"Found {driver.fours} 4xx")
        logger.warning(f"Found {driver.fives} 5xx")
        logger.warning(f"Crawled {driver.crawled} URLs")

        
