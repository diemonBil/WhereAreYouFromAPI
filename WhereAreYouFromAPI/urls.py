from django.urls import path, include

urlpatterns = [
    path("api/v1/", include("name_origin.urls")),
]
