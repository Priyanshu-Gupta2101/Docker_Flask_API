from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
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
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


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




def test_list_assignments_empty(client, h_teacher_1):
    # Ensure no assignments exist for teacher 1
    Assignment.query.filter_by(teacher_id=1).delete()
    db.session.commit()

    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200
    assert response.json['data'] == []

def test_list_assignments_unauthorized(client):
    response = client.get('/teacher/assignments')
    assert response.status_code == 401

def test_get_assignments_all_states(client, h_teacher_1):
    # Create assignments with different states
    for state in AssignmentStateEnum:
        assignment = Assignment(teacher_id=1, student_id=1, state=state, content="Test content")
        db.session.add(assignment)
    db.session.commit()

    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200
    data = response.json['data']
    assert len(data) >= len(AssignmentStateEnum)
    for assignment in data:
        assert assignment['teacher_id'] == 1
        assert assignment['state'] in [state.value for state in AssignmentStateEnum]

def test_grade_assignment_success(client, h_teacher_1):
    # Create a submitted assignment
    assignment = Assignment(teacher_id=1, student_id=1, state=AssignmentStateEnum.SUBMITTED, content="Test content")
    db.session.add(assignment)
    db.session.commit()

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": assignment.id,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 200
    data = response.json['data']
    assert data['grade'] == GradeEnum.A.value
    assert data['state'] == AssignmentStateEnum.GRADED.value

def test_grade_assignment_already_graded(client, h_teacher_1):
    # Create an already graded assignment
    assignment = Assignment(teacher_id=1, student_id=1, state=AssignmentStateEnum.GRADED, grade=GradeEnum.A, content="Test content")
    db.session.add(assignment)
    db.session.commit()

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": assignment.id,
            "grade": GradeEnum.B.value
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'

def test_grade_assignment_missing_fields(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={}
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'
