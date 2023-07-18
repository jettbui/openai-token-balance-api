"""
URL mappings for the Balance API.
"""
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from balance import views

router = DefaultRouter()
router.register('', views.BalanceView, basename='balance')
router.register('', views.ManageBalanceView, basename='balance')

app_name = 'balance'

urlpatterns = [
    path('', include(router.urls)),
]
