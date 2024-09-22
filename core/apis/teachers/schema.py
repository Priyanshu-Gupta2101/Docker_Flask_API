from marshmallow import Schema, fields

class TeacherSchema(Schema):
    teacher_id = fields.Int(dump_only=True)
    name = fields.Str()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)