import pytest
from django.urls import reverse
from rest_framework import status
from datetime import date, time, timedelta
from slots.models import DoctorAvaliability, Slots


@pytest.fixture
def availability(db, doctor):
    """Create a Monday availability entry for the doctor."""
    return DoctorAvaliability.objects.create(
        doctor=doctor,
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(12, 0),
        is_active=True,
    )


@pytest.fixture
def future_slot(db, doctor):
    """Create a future available slot."""
    future_date = date.today() + timedelta(days=3)
    return Slots.objects.create(
        doctor=doctor,
        date=future_date,
        start_time=time(10, 0),
        end_time=time(10, 30),
        is_booked=False,
        is_active=True,
        source=Slots.Source.MANUAL,
    )


# ── Availability endpoints ──────────────────────────────────────────


@pytest.mark.django_db
class TestDoctorAvailabilityListCreate:
    """GET/POST /slots/availability/"""

    url = reverse("availability-detail")

    def test_list_availability_as_doctor(self, api_client, doctor, availability):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_availability(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        data = {
            "doctor": doctor.id,
            "day_of_week": 2,  # Wednesday
            "start_time": "09:00",
            "end_time": "13:00",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_duplicate_day(self, api_client, doctor, availability):
        api_client.force_authenticate(user=doctor.user)
        data = {
            "doctor": doctor.id,
            "day_of_week": 0,  # Monday — already exists
            "start_time": "14:00",
            "end_time": "17:00",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patient_cannot_access(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDoctorAvailabilityDetail:
    """GET/PATCH/DELETE /slots/availability/<pk>/"""

    def test_retrieve_availability(self, api_client, doctor, availability):
        api_client.force_authenticate(user=doctor.user)
        url = f"/slots/availability/{availability.pk}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == availability.pk

    def test_patch_availability(self, api_client, doctor, availability):
        api_client.force_authenticate(user=doctor.user)
        url = f"/slots/availability/{availability.pk}/"
        response = api_client.patch(
            url, {"start_time": "10:00"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["start_time"] == "10:00:00"

    def test_delete_availability(self, api_client, doctor, availability):
        api_client.force_authenticate(user=doctor.user)
        url = f"/slots/availability/{availability.pk}/"
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DoctorAvaliability.objects.filter(pk=availability.pk).exists()


# ── Generate slots endpoint ─────────────────────────────────────────


@pytest.mark.django_db
class TestGenerateSlots:
    """POST /slots/generate/"""

    url = reverse("slots-generate")

    def test_generate_as_doctor(self, api_client, doctor, availability, mocker):
        mocker.patch("slots.views.generate_slots_for_doctor_task.delay")
        api_client.force_authenticate(user=doctor.user)
        response = api_client.post(self.url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "days_ahead" in response.data

    def test_generate_custom_days(self, api_client, doctor, availability, mocker):
        mocker.patch("slots.views.generate_slots_for_doctor_task.delay")
        api_client.force_authenticate(user=doctor.user)
        response = api_client.post(f"{self.url}?days_ahead=7")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["days_ahead"] == 7

    def test_generate_invalid_days(self, api_client, doctor, mocker):
        mocker.patch("slots.views.generate_slots_for_doctor_task.delay")
        api_client.force_authenticate(user=doctor.user)
        response = api_client.post(f"{self.url}?days_ahead=100")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patient_cannot_generate(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Manual slot creation ────────────────────────────────────────────


@pytest.mark.django_db
class TestManualSlotCreate:
    """POST /slots/manual/"""

    url = reverse("slots-manual-create")

    def test_create_manual_slot(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        future = date.today() + timedelta(days=5)
        data = {
            "date": str(future),
            "start_time": "14:00",
            "end_time": "14:30",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["source"] == "manual"

    def test_manual_slot_past_date(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        past = date.today() - timedelta(days=1)
        data = {
            "date": str(past),
            "start_time": "14:00",
            "end_time": "14:30",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_manual_slot_end_before_start(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        future = date.today() + timedelta(days=5)
        data = {
            "date": str(future),
            "start_time": "15:00",
            "end_time": "14:00",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patient_cannot_create_manual_slot(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        future = date.today() + timedelta(days=5)
        data = {
            "date": str(future),
            "start_time": "14:00",
            "end_time": "14:30",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── Available slots for patients ────────────────────────────────────


@pytest.mark.django_db
class TestAvailableSlots:
    """GET /slots/?doctor=<id>"""

    url = reverse("slots-available-list")

    def test_list_available_slots(self, api_client, patient_user, doctor, future_slot):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url, {"doctor": doctor.id})
        assert response.status_code == status.HTTP_200_OK

    def test_missing_doctor_param(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_doctor_cannot_browse_slots(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(self.url, {"doctor": doctor.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN
