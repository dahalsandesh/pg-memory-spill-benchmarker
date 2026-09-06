from django.db import models

class BenchmarkResult(models.Model):
    query_name = models.CharField(max_length=100)
    execution_time_ms = models.FloatField()
    ram_allocated_mb = models.IntegerField()
    spilled_to_disk = models.BooleanField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.query_name} - {self.execution_time_ms}ms"
