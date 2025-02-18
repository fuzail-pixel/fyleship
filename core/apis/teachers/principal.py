from flask import Blueprint, jsonify, request, abort
from core.models.teachers import Teacher
from core.libs.exceptions import FyleError

# Create a blueprint for principal-related APIs
blueprint = Blueprint('principal_teachers', __name__)

@blueprint.route('/principal/teachers', methods=['GET'])
def list_teachers():
    """
    List all teachers.
    Requires the 'X-Principal' header to identify the principal.
    """
    # Validate the X-Principal header
    principal_header = request.headers.get("X-Principal")
    if not principal_header:
        abort(400, description="X-Principal header is missing")

    try:
        principal_data = eval(principal_header)  # Parse the header as a dictionary
        principal_id = principal_data.get("principal_id")
        if not principal_id:
            raise FyleError(400, "Invalid X-Principal header")
    except Exception:
        abort(400, description="Invalid X-Principal header format")

    # Query all teachers from the database
    teachers = Teacher.query.all()

    # Format the response
    teacher_list = [
        {
            "id": teacher.id,
            "user_id": teacher.user_id,
            "created_at": teacher.created_at.isoformat(),
            "updated_at": teacher.updated_at.isoformat()
        }
        for teacher in teachers
    ]

    return jsonify({"data": teacher_list}), 200