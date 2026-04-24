from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import UserRegistrationView, GetDepartmentsView, MeView, DoctorView, DoctorDetailView

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", TokenBlacklistView.as_view()),
    path("auth/register/", UserRegistrationView.as_view(), name="register-user"),
    path("departments/", GetDepartmentsView.as_view(), name="department-list"),
    path("auth/me/", MeView.as_view(), name="me-user" ),
    path("doctors/", DoctorView.as_view(), name="doctor-list"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctor-detail"),

]
