"""
URL configuration for valentine_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from messages_app.views import ValentineMessageViewSet
from messages_app.views import PremiumRequestViewSet  # Import PremiumRequestViewSet

router = DefaultRouter()
router.register(r'messages', ValentineMessageViewSet, basename='messages')
router.register(r'premium-requests', PremiumRequestViewSet, basename='premium-request')  # Register new endpoint

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/', include(router.urls)),
    path('api/messages/', include('messages_app.urls')),  # Include messages_app urls
]
