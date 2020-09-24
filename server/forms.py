from marshmallow import Schema, fields
from marshmallow.validate import Length, Range, Email, Equal


class RegistrationForm(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=20))
    confirm_password = fields.Str(required=True, validate=Equal('password'))
    # birthday = fields.DateTime(required=True)
    # summary_schema = UserSchema(only=("name", "email"))


class LoginForm(Schema):
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=20))


class CrawlerForm(Schema):
    pass
