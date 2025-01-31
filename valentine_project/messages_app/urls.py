from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for any additional app-specific viewsets
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]