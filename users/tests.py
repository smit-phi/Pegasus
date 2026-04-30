from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Department, User, DoctorProfile, PatientProfile
from rest_framework import status


class DepartmentAPITest(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="Init", description="alrighty Tron, time to get started."
        )
        self.url = reverse("department-list")

    def test_get_department_list(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], self.department.name)
        self.assertEqual(response.data[0]["description"], self.department.description)
        # self.assertEqual(response.data.count(), 1)
    