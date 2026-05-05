import pytest
from django.urls import reverse
from rest_framework import status
from datetime import date, time, timedelta
from slots.models import Slots
from appointments.models import Appointment


@pytest.fixture
def future_slot(db, doctor):
    """An available slot in the future."""
    future_date = date.today() + timedelta(days=5)
    return Slots.objects.create(
        doctor=doctor,
        date=future_date,
        start_time=time(10, 0),
        end_time=time(10, 30),
        is_booked=False,
        is_active=True,
        source=Slots.Source.MANUAL,
    )


@pytest.fixture
def another_future_slot(db, doctor):
    """A second available slot on a different date."""
    future_date = date.today() + timedelta(days=6)
    return Slots.objects.create(
        doctor=doctor,
        date=future_date,
        start_time=time(11, 0),
        end_time=time(11, 30),
        is_booked=False,
        is_active=True,
        source=Slots.Source.MANUAL,
    )


@pytest.fixture
def appointment(db, patient_user, future_slot, mocker):
    """A pending appointment (mocks the Celery email task)."""
    mocker.patch("appointments.tasks.send_booking_confirmation_email.delay")
    appt = Appointment.objects.create(
        patient=patient_user,
        slot=future_slot,
        reason_for_visit="Routine checkup",
    )
    return appt


# ── Create appointment ──────────────────────────────────────────────


@pytest.mark.django_db
class TestAppointmentCreate:
    """POST /appointments/"""

    url = reverse("create-appointment")

    def test_create_appointment(self, api_client, patient_user, future_slot, mocker):
        mocker.patch("appointments.tasks.send_booking_confirmation_email.delay")
        api_client.force_authenticate(user=patient_user.user)
        data = {
            "slot": future_slot.id,
            "reason_for_visit": "Headache",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_cannot_book_already_booked_slot(
        self, api_client, patient_user, appointment, another_future_slot, mocker
    ):
        mocker.patch("appointments.tasks.send_booking_confirmation_email.delay")
        # The `appointment` fixture already booked `future_slot`.
        # Try booking a slot on the same date with a different patient
        # or re-book the same slot.
        api_client.force_authenticate(user=patient_user.user)
        data = {"slot": appointment.slot.id}
        response = api_client.post(self.url, data, format="json")
        # Slot is already booked so it won't appear in the queryset filter
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_doctor_cannot_create_appointment(self, api_client, doctor, future_slot):
        api_client.force_authenticate(user=doctor.user)
        data = {"slot": future_slot.id}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create(self, api_client, future_slot):
        data = {"slot": future_slot.id}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── Pending appointments (doctor) ───────────────────────────────────


@pytest.mark.django_db
class TestPendingAppointments:
    """GET /appointments/pending/"""

    url = reverse("pending-appointments-view")

    def test_list_pending_as_doctor(self, api_client, doctor, appointment):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_patient_cannot_see_pending(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Approve appointment ─────────────────────────────────────────────


@pytest.mark.django_db
class TestApproveAppointment:
    """POST /appointments/<pk>/approve/"""

    def test_approve_appointment(self, api_client, doctor, appointment, mocker):
        mocker.patch("appointments.tasks.send_appointment_approved_email.delay")
        api_client.force_authenticate(user=doctor.user)
        url = reverse("approve-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_patient_cannot_approve(self, api_client, patient_user, appointment):
        api_client.force_authenticate(user=patient_user.user)
        url = reverse("approve-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Reject appointment ──────────────────────────────────────────────


@pytest.mark.django_db
class TestRejectAppointment:
    """POST /appointments/<pk>/reject/"""

    def test_reject_appointment(self, api_client, doctor, appointment, mocker):
        mocker.patch("appointments.tasks.send_appointment_rejected_email.delay")
        api_client.force_authenticate(user=doctor.user)
        url = reverse("reject-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url, {"rejection_note": "Not available"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"

    def test_patient_cannot_reject(self, api_client, patient_user, appointment):
        api_client.force_authenticate(user=patient_user.user)
        url = reverse("reject-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Appointment history (doctor) ────────────────────────────────────


@pytest.mark.django_db
class TestAppointmentHistory:
    """GET /appointments/history/"""

    url = reverse("appointment-history")

    def test_doctor_sees_history(self, api_client, doctor, appointment):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_patient_cannot_see_history(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Patient appointments ────────────────────────────────────────────


@pytest.mark.django_db
class TestPatientAppointments:
    """GET /appointments/mine/"""

    url = reverse("patient-appointments")

    def test_patient_sees_own(self, api_client, patient_user, appointment):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_doctor_cannot_access(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Cancel appointment ──────────────────────────────────────────────


@pytest.mark.django_db
class TestCancelAppointment:
    """POST /appointments/<pk>/cancel/"""

    def test_cancel_own_appointment(self, api_client, patient_user, appointment):
        api_client.force_authenticate(user=patient_user.user)
        url = reverse("cancel-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "cancelled"

    def test_doctor_cannot_cancel(self, api_client, doctor, appointment):
        api_client.force_authenticate(user=doctor.user)
        url = reverse("cancel-appointment", kwargs={"pk": appointment.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cancel_nonexistent(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        url = reverse("cancel-appointment", kwargs={"pk": 9999})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
