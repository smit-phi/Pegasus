from rest_framework import serializers
from . models import DoctorAvaliability, Slots
from users.models import DoctorProfile
from users.serializers import DoctorProfileSerializer

class DoctorAvailabilitySerializer(serializers.ModelSerializer):

    doctor = DoctorProfileSerializer(read_only=True)
    class Meta:
        model = DoctorAvaliability
        fields = ["id", "doctor", "day_of_week", "start_time", "end_time", "is_active"]
        read_only_fields = ["id", "doctor", "day_of_week", "start_time", "end_time"]

        