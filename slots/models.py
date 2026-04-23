from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class DoctorAvaliability(models.Model):

    class Day(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thurday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"


    doctor = models.ForeignKey("users.DoctorProfile", on_delete=models.CASCADE, related_name="availbilities")
    day_of_week = models.IntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ('doctor', 'day_of_week')
        ordering = ["day_of_week", "start_time"]
        verbose_name_plural = "Doctor avaliabilities"


    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("end_time must be after start_time.")
            

    def __str__(self):
        return f"Dr. {self.doctor.user.get_full_name()} — {self.get_day_of_week_display()} {self.start_time}–{self.end_time}"

class Slots(models.Model):

    class Source(models.TextChoices):
        AUTO   = "auto",   "Auto-generated"
        MANUAL = "manual", "Manually added"


    doctor = models.ForeignKey("users.DoctorProfile", on_delete=models.RESTRICT, related_name="slots")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    source = models.CharField(choices= Source.choices, default=Source.AUTO)


    class Meta:
        unique_together = ("doctor", "date", "start_time")
        ordering = ["date", "start_time"]


    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("end_time must be after start_time.")
            

    def __str__(self):
        status = "booked" if self.is_booked else "free"
        return f"Dr. {self.doctor.user.get_full_name()} | {self.date} {self.start_time}–{self.end_time} [{status}]"