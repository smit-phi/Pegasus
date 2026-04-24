from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile, Department
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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]


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

    email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = ["full_name", "email", "department_name", "degree", "slot_duration"]
        read_only_fields = ["full_name", "email", "department_name", "degree", "slot_duration"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    

