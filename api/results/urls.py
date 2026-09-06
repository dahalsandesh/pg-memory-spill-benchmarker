from django.urls import path
from .views import BenchmarkResultListCreate

urlpatterns = [
    path('results/', BenchmarkResultListCreate.as_view(), name='results-list-create'),
]
