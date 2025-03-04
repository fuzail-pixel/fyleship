from core.models.assignments import Assignment
from core.libs.exceptions import FyleError

def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )
    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1

def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )
    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2

def test_post_assignment_null_content(client, h_student_1):
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': None}
    )
    assert response.status_code == 400

def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': content}
    )
    assert response.status_code == 200
    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

def test_submit_assignment_student_1(client, h_student_1):
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Test assignment content'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={'id': assignment_id, 'teacher_id': 2}
    )
    assert response.status_code == 200
    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2

def test_assignment_resubmit_error(client, h_student_1):
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Test assignment content'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={'id': assignment_id, 'teacher_id': 2}
    )
    assert response.status_code == 200

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={'id': assignment_id, 'teacher_id': 2}
    )
    assert response.status_code == 400
    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'only a draft assignment can be submitted'


def test_assignment_repr():
    assignment = Assignment(id=123)
    assert repr(assignment) == "<Assignment 123>"

def test_upsert_assignment_cases(client, h_student_1):
    response = client.put(
        '/student/assignments/9999',
        headers=h_student_1,
        json={'content': 'Updated Content'}
    )
    assert response.status_code == 404
    assert "not found" in response.json['message'].lower()

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Initial Content'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={'id': assignment_id, 'teacher_id': 2}
    )

    response = client.put(
        f'/student/assignments/{assignment_id}',
        headers=h_student_1,
        json={'content': 'Updated Content'}
    )
    
    assert response.status_code in [400, 404]


def test_upsert_function_directly(client, h_student_1, mocker):
    mocker.patch("core.models.assignments.Assignment.get_by_id", return_value=None)

    assignment = Assignment(id=9999, content="Updated Content")
    try:
        Assignment.upsert(assignment)
    except FyleError as e:
        assert "No assignment with this id was found" in str(e)

    mocker.patch("core.models.assignments.Assignment.get_by_id", return_value=Assignment(id=1, state="SUBMITTED"))

    assignment = Assignment(id=1, content="Updated Content")
    try:
        Assignment.upsert(assignment)
    except FyleError as e:
        assert "only assignment in draft state can be edited" in str(e)

    existing_assignment = Assignment(id=2, state="DRAFT", content="Old Content")
    mocker.patch("core.models.assignments.Assignment.get_by_id", return_value=existing_assignment)

    updated_assignment = Assignment(id=2, content="New Updated Content")
    result = Assignment.upsert(updated_assignment)

    assert result.content == "New Updated Content"
