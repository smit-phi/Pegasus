from rest_framework import serializers
from . models import DoctorAvaliability, Slots
from users.models import DoctorProfile
from datetime import date
from rest_framework.validators import UniqueTogetherValidator

class DoctorAvailabilitySerializer(serializers.ModelSerializer):

    # will provide read only string of the day for human readable format.
    day_display = serializers.CharField(
        source="get_day_of_week_display",
        read_only=True
    )

    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = DoctorAvaliability
        fields = [
            "id", "doctor", "day_of_week", "day_display", "start_time", "end_time", "is_active"
        ]
        read_only_fields = ["id"]

        validators = [
            UniqueTogetherValidator(
                queryset=DoctorAvaliability.objects.all(),
                fields=['doctor', 'day_of_week'],
                message="This doctor already has availability set for this day."
            )
        ]

    def validate(self, data):
        start = data.get("start_time")
        end = data.get("end_time")

        if start and end and end <= start:
            raise serializers.ValidationError(
               {"end_time": "end_time must be after start_time."}
            )
        
        # if isinstance(data.get('doctor'), type(self.context['request'].user)):
        #     data['doctor'] = data['doctor'].doctor_profile
        
        # For PATCH, start or end might not be in data at all
        # because the client only sent one of them. In that case we fall back to
        # the instance's existing values to still perform the check.
        if self.instance:
            start = start or self.instance.start_time
            end   = end   or self.instance.end_time
            if end <= start:
                raise serializers.ValidationError(
                    {"end_time": "end_time must be after start_time."}
                )

        return data
    


class SlotReadSerializer(serializers.ModelSerializer):

    doctor_name = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = Slots
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "doctor_id",
            "doctor_name",
            "department_name",
        ]

    def get_doctor_id(self, obj):
        return obj.doctor.id

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_department_name(self, obj):
        return obj.doctor.department.name if obj.doctor.department else None
    

class ManualSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slots
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "is_booked",
            "is_active",
            "source"
        ]
        # doctor is set in perform_create() on the view — same pattern as availability.
        # source is forced to "manual" in perform_create() — the client doesn't set it.
        # is_booked defaults to False — a newly created slot is always free.
        read_only_fields = [
            "id", "is_booked", "is_active", "source"
        ]

    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Slot date cannot be in the past.")
        return value
    
    def validate(self, data):
        start = data.get("start_time")
        end   = data.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time"}
            )
        return data
        
