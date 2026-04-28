from celery import shared_task

@shared_task(bind=True)
def generate_slots_for_all_doctor_task(self, days_ahead: int= 14):

    from .generator import generate_slots_for_all_doctors

    generate_slots_for_all_doctors(days_ahead=days_ahead)


@shared_task(bind=True)
def generate_slots_for_doctor_task(self, doctor_id: int, days_ahead : int = 14):
    from .generator import generate_slots_for_doctor
    from users.models import DoctorProfile

    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
    except DoctorProfile.DoesNotExist:
        return

    generate_slots_for_doctor(doctor, days_ahead=days_ahead)
