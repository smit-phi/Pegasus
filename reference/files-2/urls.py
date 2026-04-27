from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PatientRegisterView, MeView

urlpatterns = [
    path("register/",      PatientRegisterView.as_view(), name="patient-register"),
    path("login/",         TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(),   name="token-refresh"),
    path("me/",            MeView.as_view(),              name="me"),
]
