from django.urls import path
from .views import NameStatsView, PopularNamesView

urlpatterns = [
    path("names/", NameStatsView.as_view(), name="name-stats"),
    path("popular-names/", PopularNamesView.as_view(), name="popular-names"),
]
