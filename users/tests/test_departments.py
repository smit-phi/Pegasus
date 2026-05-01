import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_department_list(create_department, api_client):
    
    data = {"name": "init", "description": "alrighty Tron, time to get started."}
    department = create_department(**data)
    url = reverse("department-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["name"] == department.name
    assert response.data[0]["description"] == department.description
    
    data = {"name":554, "description": "alrighty Tron, time to get started."}
    department = create_department(**data)
    url = reverse("department-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["name"] == department.name
    assert response.data[0]["description"] == department.description


