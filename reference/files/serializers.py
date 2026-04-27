from datetime import date
from rest_framework import serializers
from .models import DoctorAvailability, Slot


# ─── DoctorAvailability serializer ───────────────────────────────────────────
#
# Handles both LIST (reading all availability entries for a doctor)
# and CREATE / UPDATE (doctor sets or edits their weekly schedule).
#
# What this serializer does NOT do:
#   - It does not generate slots. Saving availability is just saving the
#     template. Slot generation is a separate explicit action (/api/slots/generate/).
#   - It does not set the doctor field. That is done in perform_create() on the
#     view, using request.user.doctor_profile. The serializer never touches auth.
#
class DoctorAvailabilitySerializer(serializers.ModelSerializer):

    # A read-only human-readable version of the day integer.
    # day_of_week stores 0-6 in the DB. get_day_of_week_display() returns "Monday" etc.
    # source="get_day_of_week_display" tells DRF to call that method on the instance.
    # We call it() because it's a bound method — DRF will call it automatically.
    day_display = serializers.CharField(
        source="get_day_of_week_display",
        read_only=True,
    )

    class Meta:
        model  = DoctorAvailability
        fields = [
            "id",
            "day_of_week",   # integer — writable, used for create/update
            "day_display",   # string — read-only, for human-readable responses
            "start_time",
            "end_time",
            "is_active",
        ]
        read_only_fields = ["id"]
        # doctor is intentionally NOT in fields — it's injected by the view's
        # perform_create(). Keeping it out prevents a patient from crafting a
        # request that sets doctor=someone_else.

    def validate(self, data):
        # Cross-field validation always goes in validate(), not validate_<field>().
        # validate_<field>() only receives one field at a time, so it can't
        # compare start_time and end_time against each other.
        start = data.get("start_time")
        end   = data.get("end_time")

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )

        # For PATCH (partial updates), start or end might not be in data at all
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


# ─── ManualSlotSerializer ─────────────────────────────────────────────────────
#
# Used for POST /api/slots/manual/ — doctor adds a one-off slot that doesn't
# come from their weekly availability template.
#
# Key difference from availability: this writes directly to the Slot table,
# not the DoctorAvailability table. It creates the bookable row immediately.
#
class ManualSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Slot
        fields = ["id", "date", "start_time", "end_time", "is_booked", "is_active", "source"]
        read_only_fields = ["id", "is_booked", "is_active", "source"]
        # doctor is set in perform_create() on the view — same pattern as availability.
        # source is forced to "manual" in perform_create() — the client doesn't set it.
        # is_booked defaults to False — a newly created slot is always free.

    def validate_date(self, value):
        # validate_<field>() is the right tool when validating a single field
        # in isolation — no need for the full data dict.
        if value < date.today():
            raise serializers.ValidationError("Slot date cannot be in the past.")
        return value

    def validate(self, data):
        start = data.get("start_time")
        end   = data.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )
        return data


# ─── SlotReadSerializer ───────────────────────────────────────────────────────
#
# Used for GET /api/slots/?doctor=<id> — what a patient sees when browsing
# available slots for a selected doctor.
#
# Design rules:
#   1. Never expose is_booked to the patient. The queryset already filters
#      is_booked=False, so every slot in the response IS available. Sending
#      is_booked=False on every row is redundant noise.
#
#   2. Include enough info to display a useful slot card:
#      doctor name, department, date, times.
#
#   3. This serializer is entirely read-only — patients don't write slots.
#      All fields are either read_only or come from SerializerMethodField.
#
class SlotReadSerializer(serializers.ModelSerializer):

    # SerializerMethodField is always read-only — it calls get_<field_name>(self, obj)
    # where obj is the Slot instance. Use it when the data you want to expose
    # isn't a direct field on the model but needs to traverse a relation.
    doctor_name       = serializers.SerializerMethodField()
    doctor_id         = serializers.SerializerMethodField()
    department_name   = serializers.SerializerMethodField()

    class Meta:
        model  = Slot
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
        # obj.doctor is the DoctorProfile instance.
        # select_related("doctor__user", "doctor__department") in the view
        # means this doesn't fire an extra query.
        return obj.doctor.id

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()

    def get_department_name(self, obj):
        # department can be null (SET_NULL on the FK) so guard against that
        return obj.doctor.department.name if obj.doctor.department else None
