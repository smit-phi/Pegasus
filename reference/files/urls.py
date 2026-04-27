from django.urls import path
from .views import (
    DoctorAvailabilityListCreateView,
    DoctorAvailabilityDetailView,
    GenerateSlotsView,
    ManualSlotCreateView,
    AvailableSlotListView,
)

urlpatterns = [
    # Availability — doctor's weekly schedule template
    # GET  /api/slots/availability/       → list own availability entries
    # POST /api/slots/availability/       → create a new day entry
    path(
        "availability/",
        DoctorAvailabilityListCreateView.as_view(),
        name="availability-list-create",
    ),

    # GET    /api/slots/availability/<id>/  → read one entry
    # PATCH  /api/slots/availability/<id>/  → update times or is_active
    # DELETE /api/slots/availability/<id>/  → remove a day from the schedule
    path(
        "availability/<int:pk>/",
        DoctorAvailabilityDetailView.as_view(),
        name="availability-detail",
    ),

    # Slot generation — converts availability template into actual Slot rows
    # POST /api/slots/generate/             → run generator for requesting doctor
    # Optional: ?days_ahead=<int>           → defaults to 14
    path(
        "generate/",
        GenerateSlotsView.as_view(),
        name="slots-generate",
    ),

    # Manual slot — doctor adds a one-off slot directly
    # POST /api/slots/manual/
    path(
        "manual/",
        ManualSlotCreateView.as_view(),
        name="slots-manual-create",
    ),

    # Patient browsing — list available slots for a specific doctor
    # GET /api/slots/?doctor=<id>           → required query param
    path(
        "",
        AvailableSlotListView.as_view(),
        name="slots-available-list",
    ),
]
