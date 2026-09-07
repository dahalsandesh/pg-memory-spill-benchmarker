from rest_framework import generics
from .models import BenchmarkResult
from .serializers import BenchmarkResultSerializer

class BenchmarkResultListCreate(generics.ListCreateAPIView):
    serializer_class = BenchmarkResultSerializer

    def get_queryset(self):
        queryset = BenchmarkResult.objects.all()
        query_name = self.request.query_params.get('query_name', None)
        if query_name is not None:
            queryset = queryset.filter(query_name=query_name)
        return queryset
