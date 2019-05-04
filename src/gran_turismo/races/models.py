from django.db import models


class RacingSession(models.Model):

    starting_time = models.DateTimeField(verbose_name='Starting time')
    ending_time = models.DateTimeField(verbose_name='Ending time')
    successes = models.PositiveIntegerField(verbose_name='2xx')
    redirects = models.PositiveIntegerField(verbose_name='3xx')
    soft_errors = models.PositiveIntegerField(verbose_name='4xx')
    hard_errors = models.PositiveIntegerField(verbose_name='5xx')
    crawled = models.PositiveIntegerField(verbose_name='Crawled')

class RacingResult(models.Model):

    session = models.ForeignKey(RacingSession, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    status_code = models.PositiveSmallIntegerField()
