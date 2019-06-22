from django.urls import path
from . import views


urlpatterns = [
    path('detail/', views.champion_detail, name='champion_detail'),
    path('lab/', views.lab, name='lab'),
]
