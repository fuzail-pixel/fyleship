from flask import Blueprint, jsonify, request
from core.apis import decorators
from core.models.assignments import Assignment
from core.libs.exceptions import FyleError

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
    try:
        # Extract payload
        data = request.json
        assignment_id = data.get('assignment_id')  # Updated to match expected field name
        grade = data.get('grade')

        # Validate input
        if not assignment_id or grade not in ['A', 'B', 'C', 'D']:
            raise FyleError(400, "Invalid input")

        # Lookup assignment
        assignment = Assignment.get_by_id(assignment_id)
        if not assignment:
            raise FyleError(404, "Assignment not found")  # Ensure 404 for missing assignments

        # Ensure the assignment is assigned to the current teacher
        if assignment.teacher_id != p.teacher_id:
            raise FyleError(400, "This assignment is not assigned to the current teacher")

        # Ensure the assignment is in the SUBMITTED state
        if assignment.state != 'SUBMITTED':
            raise FyleError(400, "Only SUBMITTED assignments can be graded")

        # Grade the assignment using the `mark_grade` method
        graded_assignment = Assignment.mark_grade(_id=assignment_id, grade=grade, auth_principal=p)

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

    except FyleError as e:
        return jsonify({"error": e.__class__.__name__, "message": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500