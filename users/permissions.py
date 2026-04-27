from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.doctor.user


class IsAppointedDocter(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.slot.doctor.user == request.user