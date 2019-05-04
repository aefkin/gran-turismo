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
