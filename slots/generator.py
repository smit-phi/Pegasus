# Utility tool : slot generation.
from datetime import date, timedelta, datetime
from users.models import DoctorProfile
from .models import Slots, DoctorAvaliability


def generate_slots_for_doctor(doctor: DoctorProfile, from_date : date = None, days_ahead : int = 14):

    if from_date is None:
        from_date = date.today()

    to_date = from_date + timedelta(days=days_ahead)

    availabilities = DoctorAvaliability.objects.filter(doctor=doctor, is_active=True)

    if not availabilities.exists():
        return
    
    slot_duration = doctor.slot_duration

    slots_to_create = []

    current_date = from_date
    while current_date <= to_date:

        day = current_date.weekday()

        day_availabilities = [a for a in availabilities if a.day_of_week == day]

        for availability in day_availabilities:
            slot_start = datetime.combine(current_date, availability.start_time)
            window_end = datetime.combine(current_date, availability.end_time)
            while slot_start + timedelta(minutes=slot_duration) <= window_end:
                slot_end = slot_start + timedelta(minutes=slot_duration)

                slots_to_create.append(
                    Slots(
                        doctor=doctor,
                        date=current_date,
                        start_time=slot_start.time(),
                        end_time=slot_end.time()
                    )
                )

                slot_start = slot_end

        current_date += timedelta(days=1)

    Slots.objects.bulk_create(slots_to_create, ignore_conflicts=True)


def generate_slots_for_all_doctors(days_ahead:int=14):
    
    for doctor in DoctorProfile.objects.all():
        generate_slots_for_doctor(doctor, days_ahead=days_ahead)
