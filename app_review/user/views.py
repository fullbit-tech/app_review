from flask import Blueprint, g, request
from flask_restful import Resource, Api
from flask_jwt import current_identity, jwt_required

from app_review.user.models import User
from app_review.user.schemas import register_user_schema, user_schema
from app_review.extensions import db


user_api_bp = Blueprint('user_api', __name__)
user_api = Api(user_api_bp)


@user_api_bp.before_request
def before_request():
    g.user = current_identity


class Register(Resource):

    def post(self):
        """Register a new user"""
        data, errors = register_user_schema.load(request.get_json())
        if errors:
            return {'errors': errors}, 400
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return {'message': 'success'}


class UserAPI(Resource):

    @jwt_required()
    def get(self):
        """Get current user"""
        return user_schema.dump(g.user)

    @jwt_required()
    def delete(self):
        """Deactivate current user"""
        g.user.deactivate()
        return {}


user_api.add_resource(Register, '/register')
user_api.add_resource(UserAPI, '')
