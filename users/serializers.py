from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile, Department
from django.contrib.auth import authenticate
from django.db import transaction


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


# class UserRegistrationSerializer(serializers.ModelSerializer):
#     patient_profile = PatientProfileSerializer(required=False)
#     doctor_profile = DoctorProfileSerializer(required=False)
#     password = serializers.CharField(write_only=True, min_length=6)

#     class Meta:
#         model = User
#         fields = [
#             "email",
#             "first_name",
#             "last_name",
#             "password",
#             "role",
#             "age",
#             "sex",
#             "patient_profile",
#             "doctor_profile",
#         ]

#     def create(self, validated_data):
#         patient_data = validated_data.pop("patient_profile", None)
#         doctor_data = validated_data.pop("doctor_profile", None)

#         user = User.objects.create_user(**validated_data)

#         if patient_data:
#             PatientProfile.objects.create(user=user, **patient_data)
#         if doctor_data:
#             DoctorProfile.objects.create(user=user, **doctor_data)

#         return user


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "sex",
            "age",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "email", "role", "created_at"]


class PatientProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()

    class Meta:
        model = PatientProfile
        fields = ["id", "user", "weight", "is_insured", "blood_group", "allergies"]
        read_only_field = ["id"]

    def update(self, instance, validated_data):

        user_data = validated_data.pop("user", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance


# class DoctorListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DoctorProfile
#         fields = "__all__"


class DepartmentNestedSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()
    department = DepartmentNestedSerializer()

    # read only by default
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ["id", "user", "full_name", "department", "degree", "slot_duration"]
        read_only_fields = ["id"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance


class DoctorListSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ["id", "full_name", "email", "department_name", "degree", "slot_duration"]
        read_only_fields = [
            "id",
            "full_name",
            "email",
            "department_name",
            "degree",
            "slot_duration",
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class DoctorCreateSerializer(serializers.ModelSerializer):

    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    degree = serializers.CharField(required=False, allow_blank=True, default="")
    slot_duration = serializers.IntegerField(min_value=5, max_value=120)

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "age",
            "sex",
            "department",
            "degree",
            "slot_duration",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_slot_duration(self, value):
        allowed = [10, 15, 20, 30, 45, 60, 90, 120]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Slot duration must be one of: {allowed} minutes."
            )
        return value

    def create(self, validated_data):
        profile_data = {
            "department": validated_data.pop("department"),
            "degree": validated_data.pop("degree", ""),
            "slot_duration": validated_data.pop("slot_duration"),
        }

        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create(
                **validated_data, role=User.Role.DOCTOR
            )
            user.set_password(password)
            user.save()

            DoctorProfile.objects.create(user=user, **profile_data)

        return user

    # just to see for admin whaat was created.
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "email": instance.email,
            "full_name": instance.get_full_name(),
            "role": instance.role,
            "department": (
                instance.doctor_profile.department.name
                if instance.doctor_profile.department
                else None
            ),
            "degree": instance.doctor_profile.degree,
        }


class DoctorAppointmentCountSerializer(serializers.ModelSerializer):

    total_appointments = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ["id", "full_name", "total_appointments"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class PatientRegisterSerializer(serializers.ModelSerializer):

    weight = serializers.FloatField(required=False, allow_null=True)
    is_insured = serializers.BooleanField(required=False, default=False)
    blood_group = serializers.ChoiceField(
        choices=PatientProfile.BLOOD_GROUP_CHOICES,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    allergies = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            # User fields
            "email",
            "password",
            "first_name",
            "last_name",
            "sex",
            "age",
            # PatientProfile fields declared above
            "weight",
            "is_insured",
            "blood_group",
            "allergies",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_slot_duration(self, value):
        allowed = [10, 15, 20, 30, 45, 60, 90, 120]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Slot duration must be one of: {allowed} minutes."
            )
        return value

    def create(self, validated_data):
        profile_data = {
            "weight": validated_data.pop("weight", None),
            "is_insured": validated_data.pop("is_insured", False),
            "blood_group": validated_data.pop("blood_group", None),
            "allergies": validated_data.pop("allergies", None)
        }

        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create(
                **validated_data, role=User.Role.PATIENT
            )
            user.set_password(password)
            user.save()

            PatientProfile.objects.create(user=user, **profile_data)

        return user