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
    Failure case: assignment was submitted to teacher 1 but teacher 2 tries to grade it.
    """
    # Create an assignment assigned to teacher 1
    assignment = Assignment(
        student_id=1,
        teacher_id=1,  # Assigned to teacher 1
        content="Test assignment",
        state="SUBMITTED"
    )
    db.session.add(assignment)
    db.session.commit()

    # Attempt to grade it using teacher 2
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,  # Teacher 2 should not be able to grade this
        json={
            "assignment_id": assignment.id,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert "This assignment is not assigned to the current teacher" in data["message"]



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


def test_list_assignments_no_data(client, h_teacher_1, mocker):
    """
    Test listing assignments when no assignments exist for the teacher.
    """
    # Mock Assignment.get_assignments_by_teacher to return an empty list
    mocker.patch('core.models.assignments.Assignment.get_assignments_by_teacher', return_value=[])

    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    assert response.json['data'] == []


def test_grade_assignment_success(client, h_teacher_1):
    """
    Test successfully grading a valid assignment.
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

    # Grade the assignment
    response = client.post('/teacher/assignments/grade', json={
        "assignment_id": assignment.id,
        "grade": "A"
    }, headers=h_teacher_1)

    # Validate the response
    assert response.status_code == 200
    data = response.json['data']
    assert data['id'] == assignment.id
    assert data['grade'] == "A"
    assert data['state'] == "GRADED"


def test_grade_assignment_already_graded(client, h_teacher_1):
    """
    Test grading an assignment already in the GRADED state.
    """
    # Create a mock assignment in the GRADED state
    assignment = Assignment(
        student_id=1,
        teacher_id=1,
        content="Test assignment",
        state="GRADED",
        grade="A"
    )
    db.session.add(assignment)
    db.session.commit()

    # Attempt to grade the assignment
    response = client.post('/teacher/assignments/grade', json={
        "assignment_id": assignment.id,
        "grade": "B"
    }, headers=h_teacher_1)

    # Validate the response
    assert response.status_code == 400
    data = response.json
    assert data["error"] == "FyleError"
    assert "Only SUBMITTED assignments can be graded" in data["message"]


def test_grade_assignment_internal_error(client, h_teacher_1, mocker):
    """
    Test handling an internal server error during grading.
    """
    # Mock Assignment.mark_grade to raise an unexpected exception
    mocker.patch('core.models.assignments.Assignment.mark_grade', side_effect=Exception("Database error"))

    # Attempt to grade an assignment
    response = client.post('/teacher/assignments/grade', json={
        "assignment_id": 1,
        "grade": "A"
    }, headers=h_teacher_1)

    # Validate the response
    assert response.status_code == 500
    data = response.json
    assert data["error"] == "InternalServerError"
    assert "Database error" in data["message"]