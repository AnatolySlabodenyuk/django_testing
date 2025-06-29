import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from model_bakery import baker
from django.urls import reverse


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_retrieve_course(client, course_factory, student_factory):
    count = Course.objects.count()

    # Arrange
    students = student_factory(_quantity=3)
    course = course_factory(students=students)

    url = reverse('courses-detail', args=[course.id])

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert Course.objects.count() == count + 1

    data = response.json()
    assert data['id'] == course.id
    assert data['name'] == course.name


@pytest.mark.django_db
def test_list_courses(client, course_factory):
    count = Course.objects.count()

    # Arrange
    courses = course_factory(_quantity=3)

    url = reverse('courses-list')

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert Course.objects.count() == count + len(courses)

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(courses)


@pytest.mark.django_db
def test_filter_courses_by_id(client, course_factory):
    count = Course.objects.count()

    # Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[1]
    url = reverse('courses-list')

    # Act
    response = client.get(url, data={'id': target_course.id})

    # Assert
    assert response.status_code == 200
    assert Course.objects.count() == count + len(courses)

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    returned_course = data[0]
    assert returned_course['id'] == target_course.id
    assert returned_course['name'] == target_course.name


@pytest.mark.django_db
def test_filter_courses_by_name(client, course_factory):
    count = Course.objects.count()

    # Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[2]
    url = reverse('courses-list')

    # Act
    response = client.get(url, data={'name': target_course.name})

    # Assert
    assert response.status_code == 200
    assert Course.objects.count() == count + len(courses)

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    returned_course = data[0]
    assert returned_course['id'] == target_course.id
    assert returned_course['name'] == target_course.name


@pytest.mark.django_db
def test_create_course_success(client, student_factory):
    count = Course.objects.count()

    # Arrange
    students = student_factory(_quantity=2)
    payload = {
        'name': 'Django Advanced',
        'students': [student.id for student in students]
    }

    url = reverse('courses-list')

    # Act
    response = client.post(url, data=payload, format='json')

    # Assert
    assert response.status_code == 201
    assert Course.objects.count() == count + 1

    data = response.json()
    assert 'id' in data
    assert data['name'] == payload['name']


@pytest.mark.django_db
def test_update_course_success(client, course_factory, student_factory):
    count = Course.objects.count()

    # Arrange
    course = course_factory(name='Old Name')
    students = student_factory(_quantity=2)

    url = reverse('courses-detail', args=[course.id])
    updated_data = {
        'name': 'New Updated Name',
        'students': [student.id for student in students]
    }

    # Act
    response = client.put(url, data=updated_data, format='json')

    # Assert
    assert response.status_code == 200
    assert Course.objects.count() == count + 1

    data = response.json()
    assert data['id'] == course.id
    assert data['name'] == updated_data['name']
    assert set(data['students']) == set(updated_data['students'])


@pytest.mark.django_db
def test_delete_course_success(client, course_factory):
    # Arrange
    course = course_factory()
    count = Course.objects.count()

    url = reverse('courses-detail', args=[course.id])

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1
