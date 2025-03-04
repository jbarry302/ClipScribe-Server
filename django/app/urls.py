from django.urls import path
from .views import (
    transcribe
)

app_name = 'app'

urlpatterns = [
    path('transcribe/', transcribe, name='transcribe'),
]