from django.urls import path
from .views import (
    AppointmentCreateView, 
    AppointmentListView, 
    ApproveAppointmentView, 
    RejectApppintmemtView,
    AppointmentsHistory
    )

urlpatterns = [
    path("", AppointmentCreateView.as_view(), name="create-appointment"),

    path("pending/", AppointmentListView.as_view(), name="pending-appointments-view"),

    path("<int:pk>/approve/", ApproveAppointmentView.as_view(), name="approve-appointment"),

    path("<int:pk>/reject/", RejectApppintmemtView.as_view(), name="reject-appointment"),
    
    path("history/",  AppointmentsHistory.as_view(), name="appointment-history"),
]