from django.urls import path, include
from drf_spectacular.views import SpectacularRedocView, SpectacularAPIView

from .views import PasteListCreateAPIView, PasteRetrieveUpdateDestroyAPIView, LanguageListAPIView

urlpatterns = [
    path('pastes/', PasteListCreateAPIView.as_view(), name='paste-list-create'),
    path('auth/',include('dj_rest_auth.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('pastes/<str:pk>/', PasteRetrieveUpdateDestroyAPIView.as_view(), name='paste-detail'),
    path('languages/', LanguageListAPIView.as_view(), name='language-list'),
]
