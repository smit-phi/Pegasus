import pytest
from users.models import User, PatientProfile, DoctorProfile, Department


@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="securepass123",
            first_name="Test",
            last_name="User",
            role=User.Role.PATIENT,
        )
        assert user.email == "test@example.com"
        assert user.check_password("securepass123")
        assert user.role == "patient"
        assert user.is_patient

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="super@example.com",
            password="adminpass123",
            first_name="Super",
            last_name="Admin",
        )
        assert user.is_staff
        assert user.is_superuser

    def test_is_doctor_property(self):
        user = User.objects.create_user(
            email="doc@test.com",
            password="pass1234",
            first_name="Doc",
            last_name="Tor",
            role=User.Role.DOCTOR,
        )
        assert user.is_doctor
        assert not user.is_patient

    def test_email_required(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="test1234")

    def test_str_representation(self):
        user = User.objects.create_user(
            email="str@test.com",
            password="pass1234",
            first_name="Str",
            last_name="Test",
            role=User.Role.PATIENT,
        )
        assert "patient" in str(user)
        assert "str@test.com" in str(user)


@pytest.mark.django_db
class TestPatientProfile:

    def test_create_patient_profile(self, patient_user):
        assert patient_user.user.role == "patient"
        assert patient_user.blood_group == "O+"
        assert str(patient_user) == f"Patient: {patient_user.user.email}"


@pytest.mark.django_db
class TestDoctorProfile:

    def test_create_doctor_profile(self, doctor):
        assert doctor.user.role == "doctor"
        assert doctor.department.name == "Cardiology"
        assert doctor.slot_duration == 30
        assert "Dr." in str(doctor)