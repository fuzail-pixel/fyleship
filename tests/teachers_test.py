from core.models.assignments import Assignment
from core import db
def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    Test grading with an invalid grade value.
    """
    # Create a mock assignment in the SUBMITTED state
    assignment = Assignment(
        student_id=1,
        teacher_id=1,
        content="Test assignment",
        state="SUBMITTED"
    )
    db.session.add(assignment)
    db.session.commit()

    # Attempt to grade with an invalid grade
    response = client.post('/teacher/assignments/grade', json={
        "assignment_id": assignment.id,
        "grade": "E"  # Invalid grade
    }, headers=h_teacher_1)

    # Validate the response
    assert response.status_code == 400
    data = response.json
    assert data["error"] == "FyleError"  # Match the error type in the API
    assert "Invalid input" in data["message"]


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    Test grading a non-existent assignment.
    """
    # Attempt to grade a non-existent assignment
    response = client.post('/teacher/assignments/grade', json={
        "assignment_id": 999,  # Non-existent assignment
        "grade": "A"
    }, headers=h_teacher_1)

    # Validate the response
    assert response.status_code == 404
    data = response.json
    assert data["error"] == "FyleError"  # Match the error type in the API
    assert "Assignment not found" in data["message"]


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'
