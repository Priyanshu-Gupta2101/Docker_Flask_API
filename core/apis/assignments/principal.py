from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.models.users import User

from .schema import AssignmentSchema, AssignmentGradeSchema
from core.apis.teachers.schema import TeacherSchema

principal_resources = Blueprint('principal_resources', __name__)


@principal_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of all submitted and graded assignments"""
    if not p.principal_id:
        return APIResponse.error("Unauthorized", 401)
    
    assignments = Assignment.filter(
        Assignment.state.in_(['SUBMITTED', 'GRADED'])
    ).all()
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_dump)


@principal_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(p):
    """Returns list of all teachers"""
    if not p.principal_id:
        return APIResponse.error("Unauthorized", 401)
    
    teachers = Teacher.query.all()
    teachers_data = []
    for teacher in teachers:
        user = User.get_by_id(teacher.id)
        teacher_info = {
            'teacher_id': teacher.id,
            'name': user.username,
            'user_id': teacher.user_id,
            'created_at': teacher.created_at,
            'updated_at': teacher.updated_at
        }
        teachers_data.append(teacher_info)

    teachers_dump = TeacherSchema().dump(teachers_data, many=True)
    return APIResponse.respond(data=teachers_dump)


@principal_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""
    if not p.principal_id:
        return APIResponse.error("Unauthorized", 401)
    
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)