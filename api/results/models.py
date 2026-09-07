from django.db import models

class BenchmarkResult(models.Model):
    query_name = models.CharField(max_length=100)
    execution_time_ms = models.FloatField()
    ram_allocated_mb = models.IntegerField()
    spilled_to_disk = models.BooleanField()
    spill_type = models.CharField(max_length=50, default="none")
    sort_space_used_kb = models.IntegerField(default=0)
    hash_batches = models.IntegerField(default=1)
    temp_read_blocks = models.IntegerField(default=0)
    temp_written_blocks = models.IntegerField(default=0)
    work_mem_kb = models.IntegerField(default=2048)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.query_name} - {self.execution_time_ms}ms"
