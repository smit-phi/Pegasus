from datetime import date, timedelta, datetime
from apps.slots.models import Slot, DoctorAvailability
from apps.users.models import DoctorProfile


def generate_slots_for_doctor(doctor: DoctorProfile, from_date: date = None, days_ahead: int = 14):
    """
    Generates Slot rows for a doctor based on their DoctorAvailability entries.

    - Skips dates/times where a slot already exists (idempotent via unique_together)
    - Defaults to generating slots for the next 14 days from today

    Usage:
        from apps.slots.generators import generate_slots_for_doctor
        generate_slots_for_doctor(doctor_profile_instance)
    """
    if from_date is None:
        from_date = date.today()

    to_date = from_date + timedelta(days=days_ahead)

    # Only process active availability entries
    availabilities = DoctorAvailability.objects.filter(doctor=doctor, is_active=True)

    if not availabilities.exists():
        return

    slot_duration = doctor.slot_duration  # in minutes

    slots_to_create = []

    current_date = from_date
    while current_date <= to_date:
        # day_of_week: Monday=0 ... Sunday=6 — matches DoctorAvailability.Day choices
        day = current_date.weekday()

        day_availabilities = [a for a in availabilities if a.day_of_week == day]

        for availability in day_availabilities:
            # Walk through the availability window in slot_duration increments
            slot_start = datetime.combine(current_date, availability.start_time)
            window_end = datetime.combine(current_date, availability.end_time)

            while slot_start + timedelta(minutes=slot_duration) <= window_end:
                slot_end = slot_start + timedelta(minutes=slot_duration)

                slots_to_create.append(
                    Slot(
                        doctor=doctor,
                        date=current_date,
                        start_time=slot_start.time(),
                        end_time=slot_end.time(),
                        source=Slot.Source.AUTO,
                    )
                )

                slot_start = slot_end

        current_date += timedelta(days=1)

    # ignore_conflicts=True skips rows that violate unique_together
    # making this safe to run multiple times (idempotent)
    Slot.objects.bulk_create(slots_to_create, ignore_conflicts=True)


def generate_slots_for_all_doctors(days_ahead: int = 14):
    """
    Convenience function to regenerate slots for every doctor.
    Can be called from a management command or scheduled task.
    """
    for doctor in DoctorProfile.objects.all():
        generate_slots_for_doctor(doctor, days_ahead=days_ahead)
