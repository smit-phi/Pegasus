import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPatientRegistration:
    """POST /api/auth/register/ — public endpoint."""

    url = reverse("register-patient")

    def test_register_patient_success(self, api_client):
        data = {
            "email": "newpatient@test.com",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "Patient",
            "sex": "Male",
            "age": 25,
            "blood_group": "A+",
            "weight": 70,
            "is_insured": True,
            "allergies": "Pollen",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_duplicate_email(self, api_client, patient_user):
        data = {
            "email": patient_user.user.email,
            "password": "strongpass123",
            "first_name": "Dup",
            "last_name": "User",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        data = {
            "email": "short@test.com",
            "password": "abc",
            "first_name": "Short",
            "last_name": "Pass",
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    """POST /api/auth/login/ — JWT obtain pair."""

    def test_login_success(self, api_client, patient_user):
        data = {
            "email": patient_user.user.email,
            "password": "admin123",
        }
        response = api_client.post("/api/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client, patient_user):
        data = {
            "email": patient_user.user.email,
            "password": "wrongpassword",
        }
        response = api_client.post("/api/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """POST /api/auth/refresh/"""

    def test_refresh_token(self, api_client, patient_user):
        # First login to get tokens
        login_resp = api_client.post(
            "/api/auth/login/",
            {"email": patient_user.user.email, "password": "admin123"},
            format="json",
        )
        refresh = login_resp.data["refresh"]

        response = api_client.post(
            "/api/auth/refresh/", {"refresh": refresh}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_invalid_token(self, api_client):
        response = api_client.post(
            "/api/auth/refresh/", {"refresh": "invalid-token"}, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    """POST /api/auth/logout/ — blacklist refresh token."""

    def test_logout_success(self, api_client, patient_user):
        login_resp = api_client.post(
            "/api/auth/login/",
            {"email": patient_user.user.email, "password": "admin123"},
            format="json",
        )
        refresh = login_resp.data["refresh"]
        access = login_resp.data["access"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(
            "/api/auth/logout/", {"refresh": refresh}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMeEndpoint:
    """GET/PATCH /api/auth/me/ — authenticated profile view."""

    def test_me_patient(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == patient_user.user.email

    def test_me_doctor(self, api_client, doctor):
        api_client.force_authenticate(user=doctor.user)
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == doctor.user.email

    def test_me_unauthenticated(self, api_client):
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_patch_patient(self, api_client, patient_user):
        api_client.force_authenticate(user=patient_user.user)
        response = api_client.patch(
            "/api/auth/me/",
            {"weight": 75, "user": {"first_name": "Updated"}},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_me_admin_returns_404(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDoctorList:
    """GET /api/doctors/?department=<id>"""

    def test_list_doctors_by_department(self, api_client, doctor):
        url = reverse("doctor-list")
        response = api_client.get(url, {"department": doctor.department.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_doctors_empty_department(self, api_client, department):
        url = reverse("doctor-list")
        response = api_client.get(url, {"department": 9999})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestDoctorDetail:
    """GET /api/doctors/<pk>/"""

    def test_get_doctor_detail(self, api_client, doctor):
        url = reverse("doctor-detail", kwargs={"pk": doctor.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == doctor.pk

    def test_get_doctor_not_found(self, api_client):
        url = reverse("doctor-detail", kwargs={"pk": 9999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDoctorCreate:
    """POST /api/admin/doctors/ — admin only."""

    url = reverse("create-doctor")

    def test_create_doctor_as_admin(self, api_client, admin_user, department):
        api_client.force_authenticate(user=admin_user)
        data = {
            "email": "newdoc@test.com",
            "password": "docpass1234",
            "first_name": "New",
            "last_name": "Doctor",
            "department": department.id,
            "degree": "MBBS",
            "slot_duration": 30,
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_doctor_unauthorized(self, api_client, patient_user, department):
        api_client.force_authenticate(user=patient_user.user)
        data = {
            "email": "hackdoc@test.com",
            "password": "docpass1234",
            "first_name": "Hack",
            "last_name": "Doctor",
            "department": department.id,
            "degree": "MBBS",
            "slot_duration": 30,
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_doctor_unauthenticated(self, api_client, department):
        data = {
            "email": "anon@test.com",
            "password": "docpass1234",
            "first_name": "Anon",
            "last_name": "Doctor",
            "department": department.id,
            "degree": "MBBS",
            "slot_duration": 30,
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
