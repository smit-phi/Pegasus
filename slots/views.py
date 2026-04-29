from datetime import date
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from .serializers import DoctorAvailabilitySerializer, ManualSlotSerializer, SlotReadSerializer
from .models import DoctorAvaliability, Slots
from .generator import generate_slots_for_doctor
from users.permissions import IsDoctor, IsPatient
from rest_framework.response import Response
from rest_framework import status
from . tasks import generate_slots_for_doctor_task

# Create your views here.

class DoctorAvailabilityListCreateView(ListCreateAPIView):

    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        # A doctor should only be able to see his own avaliability.
        return DoctorAvaliability.objects.filter(doctor=self.request.user.doctor_profile)

    def perform_create(self, serializer):
        serializer.save()

class DoctorAvailabilityDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    # not PUT cuz that requires all the fields to be present
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        # Just like above, A doctor should only be able to see and mess with his own avaliability.
        return DoctorAvaliability.objects.filter(doctor=self.request.user.doctor_profile)
    

class GenerateSlotsView(APIView):
    permission_classes = [IsDoctor]

    def post(self, request):
        doctor = request.user.doctor_profile

        try:
            days_ahead = int(request.query_params.get("days_ahead", 14))
        except ValueError:
            raise ValidationError({"days_ahead": "Must be an integer."})
        
        if days_ahead < 1 or days_ahead > 90:
            raise ValidationError({"days_ahead": "Must be between 1 and 90."})
        
        before = Slots.objects.filter(doctor=doctor).count()

        generate_slots_for_doctor_task.delay(doctor.id, days_ahead=days_ahead)

        after = Slots.objects.filter(doctor=doctor).count()
        created = after - before

        return Response(
            {
                "message": "Slot generation has started in bg.",
                "days_ahead": days_ahead,
            }
            ,
            status=status.HTTP_202_ACCEPTED,
        )
    

class ManualSlotCreateView(CreateAPIView):

    serializer_class = ManualSlotSerializer
    permission_classes = [IsDoctor]

    def perform_create(self, serializer):
        serializer.save(
            doctor=self.request.user.doctor_profile,
            source=Slots.Source.MANUAL
        )


class AvailableSlotsView(ListAPIView):

    serializer_class = SlotReadSerializer
    permission_classes = [IsPatient]


    def get_queryset(self):
        doctor_id = self.request.query_params.get("doctor")

        if not doctor_id:
            raise ValidationError({"doctor": "This query parameter is required."})

        try:
            doctor_id = int(doctor_id)
        except ValueError:
            raise ValidationError({"doctor": "Must be a valid doctor ID."})
        
    
        return (
            Slots.objects.filter(
                doctor_id=doctor_id,
                is_booked=False,
                is_active=True,
                date__gte=date.today(),
            )
            .select_related("doctor__user", "doctor__department")
            .order_by("date", "start_time")
        )
    
