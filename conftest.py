import pytest
from users.models import Department, User, PatientProfile, DoctorProfile
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_department():
    def _create_department(**kwargs):
        return Department.objects.create(**kwargs)

    return _create_department


@pytest.fixture
def department(db):
    return Department.objects.create(
        name="Cardiology", description="Stay away from love."
    )


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        first_name="Super",
        last_name="Admin",
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def patient_user(db):
    user = User.objects.create_user(
        email="cameron@patient.com",
        password="admin123",
        first_name="Alison",
        last_name="Cameron",
        role=User.Role.PATIENT,
    )
    patient = PatientProfile.objects.create(
        user=user, weight=69, is_insured=True, blood_group="O+", allergies="None"
    )
    return patient


@pytest.fixture
def doctor(db, department):
    user = User.objects.create_user(
        email="wilson@doctor.com",
        password="admin123",
        first_name="James",
        last_name="Wilson",
        role=User.Role.DOCTOR,
    )
    doctor = DoctorProfile.objects.create(
        user=user, department=department, degree="MD", slot_duration=30
    )
    return doctor
