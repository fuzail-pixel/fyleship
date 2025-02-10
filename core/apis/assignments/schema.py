from marshmallow import Schema, EXCLUDE, fields, validates, ValidationError, post_load  # Add 'post_load' here
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_enum import EnumField
from core.models.assignments import Assignment, GradeEnum
from core.libs.helpers import GeneralObject

class AssignmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Assignment
        unknown = EXCLUDE  # Ignore unknown fields in the input payload

    # Fields definition
    id = auto_field(required=False, allow_none=True)  # ID is optional (auto-generated)
    content = fields.String(required=True)  # Content is required and must be a non-empty string
    created_at = auto_field(dump_only=True)  # Read-only field
    updated_at = auto_field(dump_only=True)  # Read-only field
    teacher_id = auto_field(dump_only=True)  # Read-only field
    student_id = auto_field(dump_only=True)  # Read-only field
    grade = auto_field(dump_only=True)  # Read-only field
    state = auto_field(dump_only=True)  # Read-only field

    # Custom validation for the 'content' field
    @validates('content')
    def validate_content(self, value):
        """Ensure content is not null or empty"""
        if not value or value.strip() == "":
            raise ValidationError("Content cannot be null or empty")

    # Post-load hook to create an Assignment object from the validated data
    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return Assignment(**data_dict)

class AssignmentSubmitSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields in the input payload

    id = fields.Integer(required=True, allow_none=False)  # Assignment ID is required
    teacher_id = fields.Integer(required=True, allow_none=False)  # Teacher ID is required

    # Post-load hook to create a GeneralObject from the validated data
    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return GeneralObject(**data_dict)

class AssignmentGradeSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields in the input payload

    id = fields.Integer(required=True, allow_none=False)  # Assignment ID is required
    grade = EnumField(GradeEnum, required=True, allow_none=False)  # Grade is required

    # Post-load hook to create a GeneralObject from the validated data
    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return GeneralObject(**data_dict)