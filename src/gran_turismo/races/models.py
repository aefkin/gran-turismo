from django.db import models


class RacingSession(models.Model):

    base_url = models.CharField(max_length=512, verbose_name="Starting point")
    starting_time = models.DateTimeField(verbose_name='Starting time')
    ending_time = models.DateTimeField(verbose_name='Ending time')
    successes = models.PositiveIntegerField(verbose_name='2xx')
    redirects = models.PositiveIntegerField(verbose_name='3xx')
    soft_errors = models.PositiveIntegerField(verbose_name='4xx')
    hard_errors = models.PositiveIntegerField(verbose_name='5xx')
    crawled = models.PositiveIntegerField(verbose_name='Crawled')

    def __str__(self):
        return self.base_url


class RacingResult(models.Model):

    session = models.ForeignKey(RacingSession, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    status_code = models.PositiveSmallIntegerField()
