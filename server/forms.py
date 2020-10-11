from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import Length, Email

fields.Field.default_error_messages['requires'] = 'Starred (*) fields are required'


class RegistrationForm(Schema):
    name = fields.Str(required=True)
    middlename = fields.Str()
    lastname = fields.Str()
    # birthday = fields.DateTime(required=True)
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    # email = fields.Str(required=True, validate=Email())
    country = fields.Str(required=True)
    password = fields.Str(required=True, validate=Length(min=8, max=20))
    confirm_password = fields.Str(required=True, validate=Length(min=8, max=20))
    company = fields.Str()

    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["confirm_password"] != data["password"]:
            raise ValidationError("Password must match Confirm Password")


class LoginForm(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class CrawlerForm(Schema):
    username = fields.Str(required=True)
    name = fields.Str(required=True, validate=Length(min=1))
    starting_url = fields.Str(required=True)
    column_names = fields.List(fields.Str(), required=True)
    xpaths = fields.List(fields.Str(), required=True)
    next_xpath = fields.Str()
    product_xpath = fields.Str()
    url_queries = fields.Dict()
    page_query = fields.Str()
    page_steps = fields.Int()
    last_page_xpath = fields.Str()
    last_page_arrow = fields.Str()
    search_xpath = fields.Str()
    search_terms = fields.Str()
    load_more = fields.Str()
    regex = fields.Dict()
    predefined_url_list = fields.List(fields.Str())
    error_xpaths = fields.List(fields.Str())
    chunksize = fields.Int()
    chunk = fields.Int()
