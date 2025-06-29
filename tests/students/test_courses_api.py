import pytest
from rest_framework.test import APIClient

from students.models import Course, Student


@pytest.mark.django_db
def test_example():
    # Arrange
    client = APIClient()

    student = Student.objects.create(name='Student1')
    course = Course.objects.create(name="Math")
    course.students.add(student)

    # Act
    response = client.get('/api/v1/courses/')

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == "Math"
