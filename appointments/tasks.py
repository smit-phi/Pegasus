from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# ── What is @shared_task? ─────────────────────────────────────────────────────
#
# @shared_task lets you define tasks without importing the Celery app instance
# directly. This matters because tasks.py is inside an app (appointments),
# and importing the Celery app from config.celery here would create a circular
# dependency chain: config → apps → config.
#
# @shared_task instead binds to whatever Celery app is active at runtime —
# which is the one created in config/celery.py, registered via config/__init__.py.
#
# bind=True gives the task access to `self`, which lets you:
#   - Retry on failure: self.retry(exc=exc, countdown=60)
#   - Inspect task state: self.request.id
#
# ── Why run emails as Celery tasks? ──────────────────────────────────────────
#
# SMTP calls are network I/O — they can take 1-3 seconds or fail entirely.
# If you call send_mail() directly in a view, the HTTP response is blocked
# until the email either sends or times out. The patient's booking request
# would feel slow, and a Gmail outage would break your API.
#
# With Celery: the view saves the appointment and returns 201 immediately.
# Celery picks up the email task from the Redis queue and sends it
# independently — the patient gets a fast response AND gets an email.
#


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, appointment_id: int):
    """
    Fired when a patient successfully books an appointment.
    Sends a confirmation email to the patient.
    """
    try:
        from appointments.models import Appointment

        appointment = (
            Appointment.objects
            .select_related(
                "patient__user",
                "slot__doctor__user",
                "slot__doctor__department",
            )
            .get(id=appointment_id)
        )

        patient_email = appointment.patient.user.email
        patient_name  = appointment.patient.user.get_full_name()
        doctor_name   = appointment.slot.doctor.user.get_full_name()
        department    = appointment.slot.doctor.department.name if appointment.slot.doctor.department else "—"
        date          = appointment.slot.date.strftime("%A, %d %B %Y")
        time          = appointment.slot.start_time.strftime("%I:%M %p")

        subject = "Appointment Request Received"
        message = f"""Hi {patient_name},

Your appointment request has been received and is pending confirmation.

Details:
  Doctor     : Dr. {doctor_name}
  Department : {department}
  Date       : {date}
  Time       : {time}

You will receive another email once the doctor confirms your appointment.

— Pegasus - Hospital Management System
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            fail_silently=False,
        )

    except Appointment.DoesNotExist:
        # Appointment was deleted between booking and task execution.
        # Nothing to do — don't retry.
        return

    except Exception as exc:
        # For any other failure (network error, Gmail down etc.),
        # retry up to max_retries times with an exponential backoff.
        # countdown=60 * 2**self.request.retries → 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_appointment_approved_email(self, appointment_id: int):
    """
    Fired when a doctor approves an appointment.
    """
    try:
        from appointments.models import Appointment

        appointment = (
            Appointment.objects
            .select_related(
                "patient__user",
                "slot__doctor__user",
                "slot__doctor__department",
            )
            .get(id=appointment_id)
        )

        patient_email = appointment.patient.user.email
        patient_name  = appointment.patient.user.get_full_name()
        doctor_name   = appointment.slot.doctor.user.get_full_name()
        department    = appointment.slot.doctor.department.name if appointment.slot.doctor.department else "—"
        date          = appointment.slot.date.strftime("%A, %d %B %Y")
        time          = appointment.slot.start_time.strftime("%I:%M %p")

        subject = "Appointment Confirmed ✓"
        message = f"""Hi {patient_name},

Your appointment has been confirmed.

Details:
  Doctor     : Dr. {doctor_name}
  Department : {department}
  Date       : {date}
  Time       : {time}

Please arrive 10 minutes before your scheduled time.

— Hospital Management System
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            fail_silently=False,
        )

    except Appointment.DoesNotExist:
        return

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_appointment_rejected_email(self, appointment_id: int):
    """
    Fired when a doctor rejects an appointment.
    """
    try:
        from appointments.models import Appointment

        appointment = (
            Appointment.objects
            .select_related(
                "patient__user",
                "slot__doctor__user",
            )
            .get(id=appointment_id)
        )

        patient_email   = appointment.patient.user.email
        patient_name    = appointment.patient.user.get_full_name()
        doctor_name     = appointment.slot.doctor.user.get_full_name()
        rejection_note  = appointment.rejection_note or "No reason provided."
        date            = appointment.slot.date.strftime("%A, %d %B %Y")
        time            = appointment.slot.start_time.strftime("%I:%M %p")

        subject = "Appointment Request Not Confirmed"
        message = f"""Hi {patient_name},

Unfortunately, your appointment request could not be confirmed.

Details:
  Doctor : Dr. {doctor_name}
  Date   : {date}
  Time   : {time}
  Reason : {rejection_note}

You can browse other available slots and request a new appointment.

— Hospital Management System
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            fail_silently=False,
        )

    except Appointment.DoesNotExist:
        return

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
