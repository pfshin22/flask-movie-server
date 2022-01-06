from flask_jwt_extended import get_jwt

from flask import request
from flask.json import jsonify
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from email_validator import validate_email, EmailNotValidError

from utils import hash_password, check_password

from flask_jwt_extended import create_access_token

# 로그아웃된 토큰은, 여기에 저장해 준다.
# 그러면, jwt가 알아서 토큰이 이 셋에 있는지 확인해서,
# 로그아웃 한 유저인지 판단한다.

jwt_blacklist = set()

# 로그아웃 클래스 
class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
        jti = get_jwt()['jti']
        print(jti)
        # 로그아웃된 토큰의 아이디값을, 블랙리스트에 저장한다.
        jwt_blacklist.add(jti)

        return {'result':'로그아웃 되었습니다.'}
