"""
collector.py - Take care of bringing race results into DB
"""
from itertools import islice

from . import models


class Collector:

    def __init__(self, session_id, results):
        self.results = (
            models.RacingResult(
                session_id=session_id,
                url=result[0],
                status_code=result[1],
            ) for result in results
        )
        self.batch_size = 250
        
    def collect(self):
        while True:
            batch = list(islice(self.results, self.batch_size))
            if not batch:
                break
            models.RacingResult.objects.bulk_create(batch, self.batch_size)

