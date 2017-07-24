from marshmallow import fields, Schema, ValidationError, validates

from app_review.user.models import User


class RegisterUserSchema(Schema):
    email = fields.Email()
    password = fields.Str(load_only=True)

    @validates('email')
    def validate_email(self, email):
        u = User.query.filter_by(email=email).first()
        if u:
            raise ValidationError('A User for that email already exists')


class UserSchema(Schema):
    class Meta:
        fields = ('email',)


register_user_schema = RegisterUserSchema()
user_schema = UserSchema()
