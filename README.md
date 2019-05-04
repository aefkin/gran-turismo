# Naturitas Gran Turismo

A simple crawler on steroids with web interface for reporting.

## Description

Crawl driver uses bloom filters for URL deduplication and asyncio coroutines
for concurrent requests.

## Dependencies

* docker
* docker-compose

## Set-up environment

```
$ docker-compose up --build
```

## Start the crawling race

```
$ docker-compose exec gran-turismo python manage.py startrace "https://example.com" -v 2
```

## Crawling options
```
$ usage: manage.py startrace [-h] [--max_redirects MAX_REDIRECTS]
                           [--max_engines MAX_ENGINES]
                           [--bf_expected_urls BF_EXPECTED_URLS]
                           [--bf_error_rate BF_ERROR_RATE] [--version]
                           [-v {0,1,2,3}] [--settings SETTINGS]
                           [--pythonpath PYTHONPATH] [--traceback]
                           [--no-color] [--force-color]
                           root_url

Start a crawling race

positional arguments:
  root_url              Starting point

optional arguments:
  -h, --help            show this help message and exit
  --max_redirects MAX_REDIRECTS
                        Max number of redirects to follow. Defaults to 10
  --max_engines MAX_ENGINES
                        Max number of crawling engines to start. Defatuls to 10
  --bf_expected_urls BF_EXPECTED_URLS
                        Bloom filter option. Expected number of URLs in the
                        bloom filter. Defatults to 1000
  --bf_error_rate BF_ERROR_RATE
                        Bloom filter option. Desired error rate in false
                        positives. Defaults to 0.001
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
```
