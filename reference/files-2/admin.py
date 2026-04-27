from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, PatientProfile, DoctorProfile


# ─── Custom admin forms ───────────────────────────────────────────────────────
#
# Root cause of the plaintext password bug:
#
# Django's UserCreationForm and UserChangeForm are built for the default User
# model which uses `username`. When you use a custom model with `email` as the
# login field, these forms need to know about it.
#
# More importantly — inheriting from UserCreationForm is what plugs into
# Django's password hashing pipeline. The form calls user.set_password()
# internally before saving. If you skip this and just put `password` as a
# plain field in fieldsets, Django writes whatever string you typed directly
# to the DB column — no hashing.
#
# UserCreationForm  → "Add user" page  — renders password1 + password2,
#                     validates they match, calls set_password() on save
# UserChangeForm    → "Edit user" page — renders the hashed value as a
#                     read-only display with a "change password" link,
#                     never the raw password
#
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ("email", "first_name", "last_name", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model  = User
        fields = ("email", "first_name", "last_name", "role", "sex", "age", "is_active", "is_staff")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Wire our custom forms — this is the fix
    form     = CustomUserChangeForm
    add_form = CustomUserCreationForm

    ordering        = ["email"]
    list_display    = ["email", "first_name", "last_name", "role", "is_active"]
    list_filter     = ["role", "is_active"]
    search_fields   = ["email", "first_name", "last_name"]

    # fieldsets = the EDIT page layout
    # `password` here renders Django's built-in read-only hash display widget,
    # not a plain text input — that's correct behaviour inherited from BaseUserAdmin
    fieldsets = (
        (None,            {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "sex", "age")}),
        ("Permissions",   {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
    )

    # add_fieldsets = the ADD page layout
    # password1 + password2 are rendered by UserCreationForm as two password
    # inputs that must match — Django hashes the result via set_password() before saving
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "blood_group", "is_insured"]
    search_fields = ["user__email", "user__first_name"]


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "department", "specialty", "slot_duration"]
    search_fields = ["user__email", "user__first_name"]
    list_filter   = ["department"]
