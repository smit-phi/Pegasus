from datetime import date

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    CreateAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied

from utils.permissions import IsDoctor, IsPatient
from .models import DoctorAvailability, Slot
from .serializers import DoctorAvailabilitySerializer, ManualSlotSerializer, SlotReadSerializer
from .generators import generate_slots_for_doctor


# ─── Availability CRUD ────────────────────────────────────────────────────────
#
# Two views handle the full CRUD for DoctorAvailability:
#   DoctorAvailabilityListCreateView  → GET (list) + POST (create)
#   DoctorAvailabilityDetailView      → GET (single) + PATCH (update) + DELETE
#
# Why two views instead of one ViewSet?
#   ViewSets are convenient but abstract away what's happening. Two plain
#   generic views make it explicit which HTTP methods hit which logic.
#   Once you understand generics well, switching to ViewSets is easy.
#
class DoctorAvailabilityListCreateView(ListCreateAPIView):
    serializer_class   = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        # A doctor should only ever see their own availability entries — never
        # another doctor's. We filter by request.user.doctor_profile here
        # rather than in perform_create() because this filter applies to reads too.
        #
        # request.user       → the authenticated User instance (from JWT)
        # .doctor_profile    → the related DoctorProfile (via OneToOneField
        #                      with related_name="doctor_profile" on the model)
        return DoctorAvailability.objects.filter(
            doctor=self.request.user.doctor_profile
        )

    def perform_create(self, serializer):
        # perform_create() is called by ListCreateAPIView after the serializer
        # has been validated. It's the right place to inject fields that the
        # client should never send — like who the doctor is.
        #
        # Why not let the client send doctor_id?
        #   Because then a malicious doctor could set doctor_id=someone_else
        #   and create availability entries for other doctors.
        #   Injecting from request.user makes it impossible to spoof.
        #
        # The unique_together constraint on (doctor, day_of_week) means if a
        # doctor tries to create a second Monday entry, the DB will raise an
        # IntegrityError. DRF catches this and returns a 400 automatically.
        serializer.save(doctor=self.request.user.doctor_profile)


class DoctorAvailabilityDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class   = DoctorAvailabilitySerializer
    permission_classes = [IsDoctor]

    # PATCH only — we don't want full PUT (requires all fields)
    http_method_names  = ["get", "patch", "delete"]

    def get_queryset(self):
        # Same filter as above — a doctor can only retrieve/update/delete
        # their own availability entries. If doctor A tries to access
        # /api/slots/availability/99/ and that entry belongs to doctor B,
        # this queryset returns empty → DRF returns 404 automatically.
        # This is correct: you don't tell the user "that's not yours",
        # you say "that doesn't exist" — a subtle but important security pattern.
        return DoctorAvailability.objects.filter(
            doctor=self.request.user.doctor_profile
        )


# ─── Slot Generation ──────────────────────────────────────────────────────────
#
# POST /api/slots/generate/
#
# This is an action, not a resource — it doesn't map cleanly to GET/POST/PATCH
# on a model. APIView is the right choice here: we write one post() method
# and have full control over what happens.
#
# What it does:
#   Calls generate_slots_for_doctor() from generators.py.
#   Returns how many slots exist after generation.
#
# Optional query param: ?days_ahead=30
#   Defaults to 14 if not provided.
#
class GenerateSlotsView(APIView):
    permission_classes = [IsDoctor]

    def post(self, request):
        doctor = request.user.doctor_profile

        # Read optional days_ahead from query params.
        # int() can raise ValueError if someone sends ?days_ahead=abc,
        # so we catch that and return a clear 400.
        try:
            days_ahead = int(request.query_params.get("days_ahead", 14))
        except ValueError:
            raise ValidationError({"days_ahead": "Must be an integer."})

        if days_ahead < 1 or days_ahead > 90:
            raise ValidationError({"days_ahead": "Must be between 1 and 90."})

        # Count slots before so we can report how many were newly created.
        # This is a convenience — the generator itself doesn't return a count.
        before = Slot.objects.filter(doctor=doctor).count()

        generate_slots_for_doctor(doctor, days_ahead=days_ahead)

        after   = Slot.objects.filter(doctor=doctor).count()
        created = after - before

        return Response(
            {
                "message":    f"Slot generation complete.",
                "created":    created,
                "days_ahead": days_ahead,
            },
            status=status.HTTP_200_OK,
        )


# ─── Manual Slot Addition ─────────────────────────────────────────────────────
#
# POST /api/slots/manual/
#
# Doctor adds a one-off slot — a specific date and time outside their weekly
# availability template. Goes directly into the Slot table with source="manual".
#
class ManualSlotCreateView(CreateAPIView):
    serializer_class   = ManualSlotSerializer
    permission_classes = [IsDoctor]

    def perform_create(self, serializer):
        # Same injection pattern as availability — doctor comes from the token,
        # source is forced to "manual" so it can never be faked by the client.
        serializer.save(
            doctor=self.request.user.doctor_profile,
            source=Slot.Source.MANUAL,
        )


# ─── Patient: Browse Available Slots ─────────────────────────────────────────
#
# GET /api/slots/?doctor=<id>
#
# A patient selects a doctor and sees their available upcoming slots.
#
# Filtering rules — a slot is only shown if ALL of these are true:
#   1. Belongs to the requested doctor (?doctor= param, required)
#   2. is_booked = False   (not already taken)
#   3. is_active = True    (not deactivated by the doctor)
#   4. date >= today       (no past slots)
#
# The ?doctor= param is required. Without it the endpoint returns 400
# rather than dumping every slot in the system.
#
class AvailableSlotListView(ListAPIView):
    serializer_class   = SlotReadSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        doctor_id = self.request.query_params.get("doctor")

        # Enforce that ?doctor= is always provided.
        # Returning all slots without a doctor filter would leak availability
        # data across all doctors — bad for privacy and performance.
        if not doctor_id:
            raise ValidationError({"doctor": "This query parameter is required."})

        # Validate it's a real integer before hitting the DB.
        try:
            doctor_id = int(doctor_id)
        except ValueError:
            raise ValidationError({"doctor": "Must be a valid doctor ID."})

        return (
            Slot.objects
            .filter(
                doctor_id=doctor_id,
                is_booked=False,
                is_active=True,
                date__gte=date.today(),      # gte = greater than or equal to
            )
            # select_related fetches doctor + user + department in one SQL JOIN
            # instead of firing separate queries for each slot row.
            # Without this: 1 query to get slots + N queries to get doctor info.
            # With this: 1 query total.
            .select_related("doctor__user", "doctor__department")
            .order_by("date", "start_time")
        )
