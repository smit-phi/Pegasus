import pytest
from datetime import date, time, timedelta
from appointments.models import Appointment
from appointments.tasks import auto_update_past_appointments
from slots.models import Slots


@pytest.fixture
def past_slot(db, doctor):
    """A slot from yesterday."""
    return Slots.objects.create(
        doctor=doctor,
        date=date.today() - timedelta(days=1),
        start_time=time(10, 0),
        end_time=time(10, 30),
        is_booked=True,
        is_active=True,
        source=Slots.Source.MANUAL,
    )


@pytest.fixture
def past_unbooked_slot(db, doctor):
    """An unbooked slot from yesterday that should be deactivated."""
    return Slots.objects.create(
        doctor=doctor,
        date=date.today() - timedelta(days=1),
        start_time=time(14, 0),
        end_time=time(14, 30),
        is_booked=False,
        is_active=True,
        source=Slots.Source.MANUAL,
    )


@pytest.fixture
def approved_past_appointment(db, patient_user, past_slot):
    """An approved appointment whose slot date is in the past."""
    return Appointment(
        patient=patient_user,
        slot=past_slot,
        status=Appointment.Status.APPROVED,
        reason_for_visit="Checkup",
    )


@pytest.fixture
def pending_past_appointment(db, patient_user, past_slot):
    """A pending appointment whose slot date is in the past."""
    return Appointment(
        patient=patient_user,
        slot=past_slot,
        status=Appointment.Status.PENDING,
        reason_for_visit="Follow-up",
    )


@pytest.mark.django_db
class TestAutoUpdatePastAppointments:
    """Tests for the nightly auto_update_past_appointments task."""

    def test_approved_becomes_completed(self, approved_past_appointment):
        # Save without triggering full_clean (which would call the email task)
        Appointment.objects.bulk_create([approved_past_appointment])
        appt = Appointment.objects.get(pk=approved_past_appointment.pk)
        assert appt.status == "approved"

        result = auto_update_past_appointments()

        appt.refresh_from_db()
        assert appt.status == "completed"
        assert result["completed"] == 1

    def test_pending_becomes_cancelled(self, pending_past_appointment):
        Appointment.objects.bulk_create([pending_past_appointment])
        appt = Appointment.objects.get(pk=pending_past_appointment.pk)
        assert appt.status == "pending"

        result = auto_update_past_appointments()

        appt.refresh_from_db()
        assert appt.status == "cancelled"
        assert result["cancelled"] == 1

    def test_expired_unbooked_slots_deactivated(self, past_unbooked_slot):
        assert past_unbooked_slot.is_active is True

        result = auto_update_past_appointments()

        past_unbooked_slot.refresh_from_db()
        assert past_unbooked_slot.is_active is False
        assert result["expired_slots"] == 1

    def test_future_appointments_untouched(self, patient_user, doctor):
        """Appointments with future slot dates should not be modified."""
        future_slot = Slots.objects.create(
            doctor=doctor,
            date=date.today() + timedelta(days=3),
            start_time=time(10, 0),
            end_time=time(10, 30),
            is_booked=True,
            is_active=True,
            source=Slots.Source.MANUAL,
        )
        appt = Appointment(
            patient=patient_user,
            slot=future_slot,
            status=Appointment.Status.APPROVED,
            reason_for_visit="Future visit",
        )
        Appointment.objects.bulk_create([appt])

        result = auto_update_past_appointments()

        appt_db = Appointment.objects.get(pk=appt.pk)
        assert appt_db.status == "approved"
        assert result["completed"] == 0

    def test_no_data_returns_zeros(self, db):
        """When there's nothing to update, all counts should be 0."""
        result = auto_update_past_appointments()
        assert result == {"completed": 0, "cancelled": 0, "expired_slots": 0}
