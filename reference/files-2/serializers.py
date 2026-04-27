from rest_framework import serializers
from .models import User, PatientProfile, DoctorProfile


# ─── User serializer (nested, reused by both profile serializers) ─────────────
#
# This is a "sub-serializer" — it's never used on its own as a view's serializer.
# Its only job is to represent the User fields that belong inside a profile response.
#
# Why nest it instead of flattening?
#   A PatientProfile row doesn't have first_name on it — that lives on User.
#   We want GET /api/auth/me/ to return one clean object with everything, so we
#   nest the user fields here and the profile fields alongside them.
#
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        # read_only=True on the whole nested serializer is set at the field level
        # below — but within this Meta we list only the fields we want to expose.
        # We never expose password, is_staff, is_superuser here.
        fields = ["id", "email", "first_name", "last_name", "sex", "age", "role", "created_at"]
        # email and role are set at registration / admin creation — they shouldn't
        # be changed through the profile endpoint, so mark them read-only here.
        read_only_fields = ["id", "email", "role", "created_at"]


# ─── PatientProfile serializer ────────────────────────────────────────────────
#
# Used for:
#   GET  /api/auth/me/   → returns the full profile (read)
#   PATCH /api/auth/me/  → updates allowed fields (write)
#
# Design decisions:
#   1. The `user` field is a nested serializer (UserNestedSerializer), not just
#      a user_id integer. This means the response looks like:
#        { "user": { "first_name": "Aisha", ... }, "weight": 58.5, ... }
#      instead of the ugly: { "user": 4, "weight": 58.5, ... }
#
#   2. We override update() to handle the nested user write. DRF does NOT
#      automatically save nested serializers — you always have to do it manually.
#      This is a key DRF rule: nested writes must be handled explicitly.
#
class PatientProfileSerializer(serializers.ModelSerializer):

    # source="user" tells DRF: when reading, get this data from self.instance.user
    # When writing (PATCH), we handle it manually in update() below.
    user = UserNestedSerializer()

    class Meta:
        model  = PatientProfile
        fields = ["id", "user", "weight", "is_insured", "blood_group", "allergies"]
        # id is auto-generated — never writable
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        # validated_data at this point looks like:
        # {
        #   "user": {"first_name": "Aisha", "sex": "female"},  ← nested dict
        #   "weight": 62.0,
        #   "blood_group": "B+"
        # }

        # Step 1: Pop the nested user data out before updating the profile.
        # If we don't pop it, ModelSerializer will try to set instance.user = {...}
        # which makes no sense — user is a related object, not a plain field.
        user_data = validated_data.pop("user", {})

        # Step 2: Update the PatientProfile fields (weight, blood_group, etc.)
        # The ** unpacks the dict: setattr(instance, "weight", 62.0), etc.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Step 3: Update the related User fields if any were sent
        # same pattern — loop and setattr
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance


# ─── DoctorProfile serializer ─────────────────────────────────────────────────
#
# Used for:
#   GET  /api/auth/me/   → doctor reads their own profile
#   PATCH /api/auth/me/  → doctor updates allowed fields
#   GET  /api/doctors/   → patients read doctor cards (same serializer, read-only context)
#
# Design decisions:
#   1. department is exposed as a nested object (id + name) not just an integer ID.
#      This is intentional — the frontend needs the name to display, not just the PK.
#      But it is read-only here: doctors don't change their own department.
#      Department assignment is an admin operation.
#
#   2. department_id is a separate write-only field used by the admin creation
#      serializer (DoctorCreateSerializer, written in Phase 5). It's not on this
#      serializer — that keeps this serializer focused on profile reads/updates.
#
class DepartmentNestedSerializer(serializers.Serializer):
    # A minimal inline serializer for the department — we don't import
    # DepartmentSerializer from another app here to avoid circular imports.
    # This is intentionally lightweight: just id and name for display.
    id   = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DoctorProfileSerializer(serializers.ModelSerializer):

    user       = UserNestedSerializer()
    department = DepartmentNestedSerializer(read_only=True)

    # A computed field — not on the model, derived from user.get_full_name()
    # SerializerMethodField is always read-only by nature.
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = DoctorProfile
        fields = [
            "id", "user", "full_name",
            "department", "specialty", "degree", "slot_duration"
        ]
        read_only_fields = ["id", "department"]

    def get_full_name(self, obj):
        # obj is the DoctorProfile instance
        # obj.user is the related User instance (one DB query unless select_related is used)
        return obj.user.get_full_name()

    def update(self, instance, validated_data):
        # Exactly the same pattern as PatientProfileSerializer.update().
        # Pop nested user data, update profile fields, then update user fields.
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


# ─── PatientRegisterSerializer ────────────────────────────────────────────────
#
# Used for POST /api/auth/register/
#
# Takes everything needed to create a User + PatientProfile in one request.
# The signal (signals.py) auto-creates a bare PatientProfile on User creation,
# but this serializer also writes the profile fields (weight, blood_group etc.)
# in the same call so the patient doesn't need a second PATCH to fill them in.
#
# Password handling:
#   `password` uses write_only=True — it's accepted on input but never
#   included in the response. You never want to return a password, even hashed.
#   We call user.set_password() explicitly in create() which runs the hashing.
#   If you just did User.objects.create(password=value), it would store plaintext.
#
class PatientRegisterSerializer(serializers.ModelSerializer):
    # Profile fields — these belong to PatientProfile, not User.
    # We declare them here so the client sends one flat JSON object.
    # We handle the split manually in create().
    weight      = serializers.FloatField(required=False, allow_null=True)
    is_insured  = serializers.BooleanField(required=False, default=False)
    blood_group = serializers.ChoiceField(
        choices=PatientProfile.BloodGroup.choices,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    allergies   = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = [
            # User fields
            "email", "password", "first_name", "last_name", "sex", "age",
            # PatientProfile fields declared above
            "weight", "is_insured", "blood_group", "allergies",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Step 1: Separate profile fields from user fields before creating anything.
        # These keys are declared on the serializer but don't exist on the User model —
        # passing them to User.objects.create_user() would cause a TypeError.
        profile_data = {
            "weight":      validated_data.pop("weight",      None),
            "is_insured":  validated_data.pop("is_insured",  False),
            "blood_group": validated_data.pop("blood_group", None),
            "allergies":   validated_data.pop("allergies",   None),
        }

        password = validated_data.pop("password")

        # Step 2: Create the User.
        # create_user() calls set_password() internally — this is what hashes it.
        # We force role=patient — the client never gets to set their own role.
        # A patient cannot register themselves as a doctor or admin.
        user = User.objects.create_user(
            **validated_data,
            password=password,
            role=User.Role.PATIENT,
        )

        # Step 3: The post_save signal already created a bare PatientProfile.
        # We update it with the profile fields from this request rather than
        # creating a new one (which would violate the OneToOne constraint).
        PatientProfile.objects.filter(user=user).update(**{
            k: v for k, v in profile_data.items() if v is not None
        })

        return user
