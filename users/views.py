from django.shortcuts import render
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Department, PatientProfile, DoctorProfile
from .serializers import (
    # UserRegistrationSerializer,
    DepartmentSerializer,
    DoctorProfileUpdateSerializer,
    PatientProfileUpdateSerializer,
    DoctorListSerializer,
    DoctorCreateSerializer,
    DoctorAppointmentCountSerializer,
    PatientRegisterSerializer
)
from rest_framework.views import APIView
from django.db.models import Count
from .permissions import IsAdmin
from rest_framework.response import Response


# class UserRegistrationView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegistrationSerializer


class GetDepartmentsView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "patch"]

    def get_object(self):

        user = self.request.user

        if user.role == "patient":
            try:
                return PatientProfile.objects.select_related("user").get(user=user)
            except PatientProfile.DoesNotExist:
                raise NotFound("Patient does not exist.")

        elif user.role == "doctor":
            try:
                return DoctorProfile.objects.select_related("user", "department").get(
                    user=user
                )
            except DoctorProfile.DoesNotExist:
                raise NotFound("Doctor does not exist.")

        else:
            raise PermissionDenied("Profile not avaliable for Admin")

    def get_serializer_class(self):

        user = self.request.user

        if user.role == "patient":
            return PatientProfileUpdateSerializer
        elif user.role == "doctor":
            return DoctorProfileUpdateSerializer
        else:
            raise NotFound("Profile not avaliable for Admin")

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "PATCH":
            kwargs["partial"] = True
        return super().get_serializer(*args, **kwargs)


class DoctorView(generics.ListAPIView):

    serializer_class = DoctorListSerializer

    def get_queryset(self):
        qs = DoctorProfile.objects.select_related("user", "department")
        department = self.request.query_params.get("department")
        if department:
            qs = qs.filter(department=department)
        return qs

class DoctorDetailView(generics.RetrieveAPIView):

    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorListSerializer


class DoctorCreateView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = DoctorCreateSerializer
    permission_classes = [IsAdmin]


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin]


class DoctorCountView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        doctors = DoctorProfile.objects.annotate(
            total_appointments=Count("slots__appointment")
        ).order_by("-total_appointments")

        serializer = DoctorAppointmentCountSerializer(doctors, many=True)
        return Response(serializer.data)


class PatientCreateView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = PatientRegisterSerializer
    permission_classes = [AllowAny]


