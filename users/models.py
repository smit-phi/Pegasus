from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    GENDER_CHOICES = [
        ('Male', 'Male'), 
        ('Female', 'Female'), 
    ]

    class Role(models.TextChoices):
        ADMIN   = "admin",   "Admin"
        DOCTOR  = "doctor",  "Doctor"
        PATIENT = "patient", "Patient"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    sex = models.CharField(max_length=10 ,choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']


    def __str__(self):
        return f"Patient: {self.get_email_field_name()}"
    
    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR
    
    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

class PatientProfile(models.Model):

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    weight = models.FloatField(blank=True, null=True)
    is_insured = models.BooleanField(default=False)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    allergies = models.TextField(blank=True, null=True)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, related_name="doctors")
    degree = models.CharField(max_length=50, blank=True)
    slot_duration = models.PositiveIntegerField()

    def __str__(self):
        return f"Dr. {self.get_full_name() - {self.department}}"
