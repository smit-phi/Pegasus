from django.urls import path
from .views import (
    AppointmentCreateView, 
    AppointmentListView, 
    ApproveAppointmentView, 
    RejectApppintmemtView,
    AppointmentsHistory,
    PatientAppointments,
    CancelAppointment
    )

urlpatterns = [
    path("", AppointmentCreateView.as_view(), name="create-appointment"),

    path("pending/", AppointmentListView.as_view(), name="pending-appointments-view"),

    path("<int:pk>/approve/", ApproveAppointmentView.as_view(), name="approve-appointment"),

    path("<int:pk>/reject/", RejectApppintmemtView.as_view(), name="reject-appointment"),
    
    path("history/",  AppointmentsHistory.as_view(), name="appointment-history"),

    path("mine/", PatientAppointments.as_view(), name="patient-appointments"),

    path("<int:pk>/cancel/", CancelAppointment.as_view(), name="cancel-appointment"),
]

