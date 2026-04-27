from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from rest_framework.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
                raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def  create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):

    GENDER_CHOICES = [
        ('Male', 'Male'), 
        ('Female', 'Female'), 
    ]

    class Role(models.TextChoices):
        ADMIN   = "admin",   "Admin"
        DOCTOR  = "doctor",  "Doctor"
        PATIENT = "patient", "Patient"

    objects = UserManager()

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    sex = models.CharField(max_length=10 ,choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']


    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR
    
    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT
    
    def __str__(self):
        return f"{self.role}: {self.email}"

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

    def __str__(self):
        return f"Patient: {self.user.email}"


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


    def clean(self):
        if self.user.role != "doctor":
            raise ValidationError("user must be with doctor role")

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.department}"
