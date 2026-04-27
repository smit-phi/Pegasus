from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PatientProfile, DoctorProfile, User
from .serializers import (
    PatientProfileSerializer,
    DoctorProfileSerializer,
    PatientRegisterSerializer,
)


# ─── POST /api/auth/register/ ─────────────────────────────────────────────────
#
# Patient self-registration. No authentication required — the user doesn't
# have a token yet, that's why they're registering.
#
# After successful registration we return JWT tokens immediately so the
# client is logged in right away without needing a second /login/ call.
#
class PatientRegisterView(CreateAPIView):
    serializer_class   = PatientRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer.save() calls our create() which returns the User instance
        user = serializer.save()

        # Generate JWT token pair so the client is logged in immediately —
        # no need for a separate POST /login/ call after registration
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id":         user.id,
                    "email":      user.email,
                    "first_name": user.first_name,
                    "last_name":  user.last_name,
                    "role":       user.role,
                },
                "tokens": {
                    "access":  str(refresh.access_token),
                    "refresh": str(refresh),
                }
            },
            status=status.HTTP_201_CREATED,
        )


# ─── GET + PATCH /api/auth/me/ ────────────────────────────────────────────────
#
# RetrieveUpdateAPIView gives us two HTTP methods for free:
#   GET   → calls get_object() then serializes it       → 200
#   PATCH → partial update, only sent fields change     → 200
#
# Why one endpoint for both patient and doctor?
#   Both users hit the same /me/ URL. Inside get_object() we branch on the
#   user's role and return the correct profile. This keeps the URL surface
#   clean — the client doesn't need to know /patient-profile/ vs /doctor-profile/.
#
class MeView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names  = ["get", "patch"]

    def get_object(self):
        user = self.request.user

        if user.role == "patient":
            try:
                return PatientProfile.objects.select_related("user").get(user=user)
            except PatientProfile.DoesNotExist:
                raise NotFound("Patient profile not found.")

        elif user.role == "doctor":
            try:
                return DoctorProfile.objects.select_related("user", "department").get(user=user)
            except DoctorProfile.DoesNotExist:
                raise NotFound("Doctor profile not found.")

        else:
            raise NotFound("Profile not available for admin users.")

    def get_serializer_class(self):
        user = self.request.user
        if user.role == "patient":
            return PatientProfileSerializer
        elif user.role == "doctor":
            return DoctorProfileSerializer
        else:
            raise NotFound("Profile not available for admin users.")

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "PATCH":
            kwargs["partial"] = True
        return super().get_serializer(*args, **kwargs)
