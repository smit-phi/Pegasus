from rest_framework import serializers
from .models import Appointment
from datetime import date
from slots.models import Slots


class SlotSummarySerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = Slots
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "doctor_name",
            "department_name",
        ]

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_department_name(self, obj):
        return obj.doctor.department.name if obj.doctor.department else None


class AppointmentCreateSerializer(serializers.ModelSerializer):

    slot = serializers.PrimaryKeyRelatedField(
        queryset=Slots.objects.filter(is_booked=False, is_active=True)
    )

    slot_detail = SlotSummarySerializer(source="slot", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "slot",
            "slot_detail",
            "reason_for_visit",
            "status",
            "created_at",
        ]

    def validate_slot(self, slot):

        if slot.date < date.today():
            raise serializers.ValidationError(
                "the selected slot is of the past and can't be booked now."
            )

        return slot

    def validate(self, data):
        request = self.context.get("request")
        if request and hasattr(request.user, "patient_profile"):
            slot = data.get("slot")
            if slot:
                already_booked = Appointment.objects.filter(
                    patient=request.user.patient_profile,
                    slot__date=slot.date,
                    status__in=[
                        Appointment.Status.PENDING,
                        Appointment.Status.APPROVED,
                    ],
                ).exists()
                if already_booked:
                    raise serializers.ValidationError(
                        "You already have a pending or approved appointment on this date."
                    )
        return data


class AppointmentDetailSerializer(serializers.ModelSerializer):

    patient_name = serializers.SerializerMethodField()
    slot_detail = SlotSummarySerializer(source="slot", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "slot",
            "slot_detail",
            "status",
            "reason_for_visit",
            "rejection_note",
            "created_at",
        ]

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    