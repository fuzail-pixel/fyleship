from flask import Blueprint, jsonify, request
from core.apis import decorators
from core.models.assignments import Assignment

# Define the teacher_assignments_resources blueprint
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """
    Returns a list of assignments submitted to the teacher.
    """
    # Fetch assignments for the authenticated teacher
    teachers_assignments = Assignment.get_assignments_by_teacher(teacher_id=p.teacher_id)

    # Serialize the assignments manually
    return jsonify({
        "data": [
            {
                "id": assignment.id,
                "content": assignment.content,
                "grade": assignment.grade,
                "state": assignment.state,
                "student_id": assignment.student_id,
                "teacher_id": assignment.teacher_id,
                "created_at": assignment.created_at.isoformat(),
                "updated_at": assignment.updated_at.isoformat()
            } for assignment in teachers_assignments
        ]
    }), 200

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.authenticate_principal
def grade_assignment(p):
    """
    Grades an assignment submitted to the teacher.
    """
    # Extract payload
    data = request.json
    assignment_id = data.get('id')
    grade = data.get('grade')

    # Validate grade
    valid_grades = ['A', 'B', 'C', 'D']
    if grade not in valid_grades:
        return jsonify({"error": "ValidationError", "message": "Invalid grade"}), 400

    # Lookup assignment
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"error": "FyleError", "message": "Assignment not found"}), 404

    # Ensure the assignment is submitted to the current teacher
    if assignment.teacher_id != p.teacher_id or assignment.state != 'SUBMITTED':
        return jsonify({"error": "FyleError", "message": "Assignment not submitted to this teacher"}), 400

    # Grade the assignment using the `mark_grade` method
    try:
        graded_assignment = Assignment.mark_grade(_id=assignment_id, grade=grade, auth_principal=p)
    except AssertionError as e:
        return jsonify({"error": "FyleError", "message": str(e)}), 400

    # Return the updated assignment
    return jsonify({
        "data": {
            "content": graded_assignment.content,
            "created_at": graded_assignment.created_at.isoformat(),
            "grade": graded_assignment.grade,
            "id": graded_assignment.id,
            "state": graded_assignment.state,
            "student_id": graded_assignment.student_id,
            "teacher_id": graded_assignment.teacher_id,
            "updated_at": graded_assignment.updated_at.isoformat()
        }
    }), 200