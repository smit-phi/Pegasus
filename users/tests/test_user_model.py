import pytest
from django.core.exceptions import ValidationError
from ..models import User, PatientProfile, DoctorProfile

@pytest.mark.django_db
class TestUserModel