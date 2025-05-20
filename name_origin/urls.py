from django.urls import path
from .views import NameStatsView

urlpatterns = [
    path('names/', NameStatsView.as_view(), name='name-stats'),
]
