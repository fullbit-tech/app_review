from marshmallow import fields, Schema, ValidationError, validates

from app_review.user.models import User, UserStatus


class RegisterUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(load_only=True, required=True)

    @validates('email')
    def validate_email(self, email):
        u = User.query.filter_by(email=email).first()
        if u:
            raise ValidationError('A User for that email already exists')


class UserSchema(Schema):
    status = fields.Function(lambda obj: UserStatus(obj.status).name)
    class Meta:
        fields = ('email', 'github_verified', 'status',
                  'github_auth_link', 'github_avatar',
                  'github_username')


register_user_schema = RegisterUserSchema()
user_schema = UserSchema()
