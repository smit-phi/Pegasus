from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "sex", "age"]


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = "__all__"


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer(required=False)
    doctor_profile = DoctorProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "age",
            "sex",
            "patient_profile",
            "doctor_profile",
        ]

    def create(self, validated_data):
        patient_data = validated_data.pop("patient_profile", None)
        doctor_data = validated_data.pop("doctor_profile", None)

        user = User.objects.create_user(**validated_data)

        if patient_data:
            PatientProfile.objects.create(user=user, **patient_data)
        if doctor_data:
            DoctorProfile.objects.create(user=user, **doctor_data)

        return user
