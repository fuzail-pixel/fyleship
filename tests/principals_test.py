from unittest.mock import patch
from core.models.assignments import AssignmentStateEnum, GradeEnum
from core.models.teachers import Teacher  # Added for teacher-related test


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


def test_get_teachers(client, h_principal):
    """
    Test the GET /api/principal/teachers endpoint.
    """
    mock_teachers = [
        Teacher(id=1, user_id=3, created_at="2023-01-01T10:00:00", updated_at="2023-01-02T10:00:00"),
        Teacher(id=2, user_id=4, created_at="2023-01-03T11:00:00", updated_at="2023-01-04T11:00:00")
    ]

    with patch("core.apis.teachers.principal.Teacher.query.all", return_value=mock_teachers):
        response = client.get(
            "/api/principal/teachers",
            headers=h_principal
        )

    assert response.status_code == 200
    data = response.json["data"]

    print("API Response Data:", data)  # Debugging print

    assert isinstance(data, list)
    assert len(data) == 2

    # Check if response matches mock data
    assert data[0]["id"] == 1
    assert data[0]["user_id"] == 3

    # Allow timestamps to be dynamic but ensure they exist
    assert "created_at" in data[0]
    assert "updated_at" in data[0]

def test_get_teachers_missing_header(client):
    """
    Test GET /api/principal/teachers with missing X-Principal header.
    """
    response = client.get("/api/principal/teachers")
    assert response.status_code == 400
    assert "X-Principal header is missing" in response.json["message"]


def test_get_teachers_invalid_header_format(client):
    """
    Test GET /api/principal/teachers with an invalid X-Principal header format.
    """
    response = client.get(
        "/api/principal/teachers",
        headers={"X-Principal": "invalid_json"}
    )
    assert response.status_code == 400
    assert "Invalid X-Principal header format" in response.json["message"]


def test_get_teachers_invalid_principal_id(client):
    """
    Test GET /api/principal/teachers with missing principal_id.
    """
    response = client.get(
        "/api/principal/teachers",
        headers={"X-Principal": '{"user_id": 5}'}
    )
    assert response.status_code == 400
    assert "Invalid X-Principal header" in response.json["message"]
