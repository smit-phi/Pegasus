from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PatientProfile, DoctorProfile


# ─── What is a signal? ────────────────────────────────────────────────────────
#
# A signal is Django's built-in event system. post_save fires automatically
# after any model's .save() completes — whether that's from the admin panel,
# the API, the shell, or a management command.
#
# This solves issue 3: PatientProfile not being created when a User is saved
# via the admin panel. Without signals, you'd have to remember to create the
# profile manually everywhere a user is created — admin, API, shell, tests.
# That's fragile. Signals make it automatic regardless of where the user
# comes from.
#
# @receiver(post_save, sender=User) means:
#   "After any User.save() call completes, run this function."
#
# The `created` argument is True only on INSERT (new row), False on UPDATE
# (existing row being edited). We only create profiles on INSERT — otherwise
# editing a user's name would try to create a duplicate profile and crash.
#
@receiver(post_save, sender=User)
def create_profile_on_user_creation(sender, instance, created, **kwargs):
    # `sender`   = the model class that fired the signal (User)
    # `instance` = the actual User object that was just saved
    # `created`  = True if this was an INSERT, False if UPDATE

    if not created:
        # User was updated (e.g. admin changed their name) — do nothing
        return

    if instance.role == User.Role.PATIENT:
        # get_or_create is safer than create() here.
        # If somehow a profile already exists (e.g. a previous failed attempt
        # left a partial row), we don't crash — we just return the existing one.
        PatientProfile.objects.get_or_create(user=instance)

    elif instance.role == User.Role.DOCTOR:
        # For doctors: we do NOT auto-create a DoctorProfile here.
        #
        # Why not? DoctorProfile requires slot_duration and department —
        # fields that have no sensible default and must be explicitly set.
        # Auto-creating a DoctorProfile with null/blank required fields would
        # either crash or create unusable data.
        #
        # Instead, doctors are created by admin via DoctorCreateSerializer
        # (Phase 5) which creates User + DoctorProfile together in one call
        # with all required fields. That's the correct flow for doctors.
        #
        # If you're creating a doctor from the Django admin panel directly,
        # you create the User first, then create the DoctorProfile separately
        # and link it — that's intentional and correct.
        pass
