from django.contrib import admin
from .models import User, DoctorProfile, Department, PatientProfile

# Register your models here.

admin.site.register(User)
admin.site.register(DoctorProfile)
admin.site.register(Department)
admin.site.register(PatientProfile)
