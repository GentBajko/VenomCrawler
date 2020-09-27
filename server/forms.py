from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Range, Email, Equal


class RegistrationForm(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=20))
    confirmpass = fields.Str(required=True)
    birthday = fields.DateTime(required=True)
    # summary_schema = UserSchema(only=("name", "email"))

    @classmethod
    @validates('confirmpass')
    def confirm_password(cls, confirmpass):
        if confirmpass != cls.password:
            raise ValidationError("The passwords don't match")


class LoginForm(Schema):
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=20))


class CrawlerForm(Schema):
    pass
