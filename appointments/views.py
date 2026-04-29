from django.shortcuts import render
from .serializers import AppointmentCreateSerializer, AppointmentDetailSerializer
from .models import Appointment
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from users.permissions import (
    IsPatient,
    IsDoctor,
    IsOwner,
    IsAppointedDocter,
    IsOwnerPatient,
)
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class AppointmentCreateView(CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsPatient]

    def perform_create(self, serializer):
        try:
            patient = self.request.user.patient_profile
        except Exception:
            raise ValidationError("Patient profile not found for this user.")

        serializer.save(patient=patient)


class AppointmentListView(ListAPIView):

    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsDoctor, IsOwner]

    def get_queryset(self):
        return Appointment.objects.filter(
            slot__doctor=self.request.user.doctor_profile,
            status=Appointment.Status.PENDING,
        )


class ApproveAppointmentView(APIView):

    permission_classes = [IsDoctor, IsAppointedDocter]

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        self.check_object_permissions(request, appointment)

        appointment.approve()
        appointment.save()

        return Response({"status": appointment.status})


class RejectApppintmemtView(APIView):

    permission_classes = [IsDoctor, IsAppointedDocter]

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        self.check_object_permissions(request, appointment)

        note = request.data.get("rejection_note")

        appointment.reject(note)
        appointment.save()

        return Response({"status": appointment.status, "rejection_note": note})


class AppointmentsHistory(ListAPIView):

    permission_classes = [IsDoctor, IsAppointedDocter]
    serializer_class = AppointmentDetailSerializer

    def get_queryset(self):
        return Appointment.objects.filter(
            slot__doctor=self.request.user.doctor_profile,
            status__in=[Appointment.Status.PENDING, Appointment.Status.APPROVED],
        ).order_by("-created_at")


class PatientAppointments(ListAPIView):

    permission_classes = [IsPatient]
    serializer_class = AppointmentDetailSerializer

    def get_queryset(self):

        return Appointment.objects.filter(
            patient=self.request.user.patient_profile
        ).order_by("-created_at")


class CancelAppointment(APIView):

    permission_classes = [IsPatient, IsOwnerPatient]

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        self.check_object_permissions(request, appointment)


        if appointment.status == Appointment.Status.PENDING or appointment.status == Appointment.Status.APPROVED:
            appointment.cancel()
            appointment.save()
            return Response({"status": appointment.status})

        else:
            return Response({"error": "cannot cancel a canceled or compelted appointment."})