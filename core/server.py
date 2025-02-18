from flask import jsonify
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import (
    student_assignments_resources,
    teacher_assignments_resources,
    principal_assignments_resources,
)
from core.apis.teachers.principal import blueprint as principal_teachers_blueprint  # Import the new blueprint
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

# Register blueprints for assignment-related APIs
app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')
app.register_blueprint(principal_assignments_resources, url_prefix='/principal')

# Register the blueprint for principal-related APIs (e.g., GET /principal/teachers)
app.register_blueprint(principal_teachers_blueprint, url_prefix='/api')  # Use '/api' as the prefix

@app.route('/')
def ready():
    """
    Health check endpoint to confirm the server is running.
    Returns the current UTC time to indicate readiness.
    """
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })
    return response

@app.errorhandler(Exception)
def handle_error(err):
    """
    Global error handler to catch and respond to exceptions.
    Handles custom errors, validation errors, database integrity errors, and generic HTTP exceptions.
    """
    if isinstance(err, FyleError):
        # Handle custom FyleError exceptions
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        # Handle Marshmallow validation errors
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        # Handle SQLAlchemy integrity errors (e.g., duplicate entries)
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        # Handle generic HTTP exceptions
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code
    # Re-raise any unhandled exceptions
    raise err