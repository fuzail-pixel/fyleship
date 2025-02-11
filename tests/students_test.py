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
    """
    failure case: content cannot be null
    """
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })
    assert response.status_code == 400

def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })
    assert response.status_code == 200
    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

def test_submit_assignment_student_1(client, h_student_1):
    # Step 1: Create a draft assignment
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Test assignment content'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    # Step 2: Submit the assignment
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2  # Simulate submitting to teacher with ID 2
        }
    )

    # Step 3: Validate the response
    assert response.status_code == 200
    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2

def test_assignment_resubmit_error(client, h_student_1):
    # Step 1: Create a draft assignment
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={'content': 'Test assignment content'}
    )
    assert response.status_code == 200
    assignment_id = response.json['data']['id']

    # Step 2: Submit the assignment
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2  # Simulate submitting to teacher with ID 2
        }
    )
    assert response.status_code == 200

    # Step 3: Attempt to resubmit the same assignment
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2
        }
    )

    # Step 4: Validate the error response
    assert response.status_code == 400
    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'only a draft assignment can be submitted'