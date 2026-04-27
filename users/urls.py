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

#  Chase:
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3NzgyOTkxNywiaWF0IjoxNzc3MjI1MTE3LCJqdGkiOiIyMTVjM2RiMDA5MzQ0ZTEwODI5OWJiNTFlMTEwOGJkZiIsInVzZXJfaWQiOiI1In0.d5n6V_OGU7j3M9QXHH4q2VaeMtBnmgm_3sgJ4krywkw",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3MjI2OTE3LCJpYXQiOjE3NzcyMjUxMTcsImp0aSI6ImQ4MzIyMTFlOTViMzRjOWFiMDNjNjVhYjRiNzkwNGVhIiwidXNlcl9pZCI6IjUifQ.-qYrsuHcPC4ZC9rQPs-cw-UPgVFE1g1IDBgfZnWg3pM"
#
