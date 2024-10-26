# webhook/urls.py
from django.urls import path
from .views import yaya_webhook

urlpatterns = [
    path("yaya-webhook/", yaya_webhook, name="yaya-webhook"),
]
