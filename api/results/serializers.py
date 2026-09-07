from rest_framework import serializers
from .models import BenchmarkResult

class BenchmarkResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkResult
        fields = '__all__'
        read_only_fields = ['id']
