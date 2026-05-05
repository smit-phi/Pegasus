import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestGetDepartmentList:
    """GET /api/departments/ — public, no auth required."""

    def test_list_returns_200(self, api_client, department):
        url = reverse("department-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_returns_created_department(self, api_client, create_department):
        create_department(name="Neurology", description="Brain stuff.")
        url = reverse("department-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        names = [d["name"] for d in response.data]
        assert "Neurology" in names

    def test_empty_list(self, api_client):
        url = reverse("department-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
