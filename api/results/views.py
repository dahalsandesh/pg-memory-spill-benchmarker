from rest_framework import generics
from .models import BenchmarkResult
from .serializers import BenchmarkResultSerializer

class BenchmarkResultListCreate(generics.ListCreateAPIView):
    queryset = BenchmarkResult.objects.all()
    serializer_class = BenchmarkResultSerializer
