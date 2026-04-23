from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING   = "pending",   "Pending"
        APPROVED  = "approved",  "Approved"
        REJECTED  = "rejected",  "Rejected"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey("users.PatientProfile", on_delete=models.CASCADE, related_name="appointments")
    slot = models.ForeignKey("slots.Slots", on_delete=models.CASCADE, related_name="appointment")
    status = models.CharField(choices=Status.choices, default=Status.PENDING)
    reason_for_visit = models.TextField(blank=True)
    rejection_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


    def clean(self):
        if self.slot.is_booked and self._state.adding:
            raise ValidationError("This slot is already booked.")


    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self._state.adding

        super().save(*args, **kwargs)
        
        if is_new:
            self.slot.is_booked = True
            self.slot.save(update_fields="is_booked")


    def approve(self):
        self.status = self.Status.APPROVED
        self.save(updated_fields=["status", "updated_at"])

    
    def reject(self, note: str = ""):
        self.status = self.Status.REJECTED
        self.rejection_note = note
        self.save(updated_fields=["status", "updated_at", "rejection_note"])

        self.slot.is_booked = False
        self.slot.save(updated_fields=["is_booked"])


    def cancel(self):
        self.status = self.Status.CANCELLED
        self.save(updated_fields=["status", "updated_at"])

        self.slot.is_booked = False
        self.slot.save(updated_fields=["is_booked"])

    
    def complete(self):
        self.status = self.Status.COMPLETED
        self.save(updated_fields=["status", "updated_at"])


    def __str__(self):
        return (
            f"{self.patient.user.get_full_name()} → "
            f"Dr. {self.slot.doctor.user.get_full_name()} | "
            f"{self.slot.date} {self.slot.start_time} [{self.status}]"
        )