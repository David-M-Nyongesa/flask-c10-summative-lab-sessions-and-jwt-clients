from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()


class NoteSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    user_id = fields.Int()


user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
