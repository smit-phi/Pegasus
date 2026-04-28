from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DoctorAvaliability


@receiver(post_save, sender=DoctorAvaliability)
def generate_slots_on_availability_save(sender, instance, **kwargs):
    """
    When a doctor creates or updates their availability, immediately generate
    slots for them rather than waiting for the nightly batch run.

    This means a doctor who sets up Monday availability at 2pm will have
    their slots visible to patients within seconds, not the next morning.

    Why .delay() and not calling the generator directly?
        The signal fires inside the HTTP request that saved the availability.
        Generating slots synchronously would add latency to that request —
        especially if the doctor has many weeks of slots to generate.
        .delay() hands it off to Celery and the response returns immediately.
    """
    from .tasks import generate_slots_for_doctor_task
    generate_slots_for_doctor_task.delay(
        doctor_id=instance.doctor.id,
        days_ahead=14,
    )
