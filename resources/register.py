from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from email_validator import validate_email, EmailNotValidError

from utils import hash_password

from flask_jwt_extended import create_access_token

class UserRegisterResource(Resource) :
    def post(self) :
        data = request.get_json()
        # email, password, name, gender

        # 2. 이메일 주소가 제대로 된 주소인지 확인하는 코드
        #    잘못된 이메일주소면, 잘못됬다고 응답한다.
        try:
            # Validate.
            validate_email(data['email'])
            
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error' : '이메일 주소가 잘못되었습니다.'} ,HTTPStatus.BAD_REQUEST

        # 3. 비밀번호 길이같은 조건이 있는지 확인하는 코드
        #    잘못됬으면, 클라이언트에 응답한다.
        if len( data['password'] ) < 4 or len(data['password']) > 10 :
            return {'error' : '비번 길이 확인하세요'}, HTTPStatus.BAD_REQUEST

        # 4. 비밀번호를 암호화한다.
        hashed_password = hash_password(data['password'])

        print(hashed_password)
        print('암호화된 비번 길이 ' + str( len(hashed_password) ))

        # 5. 데이터를 DB에 저장한다.
        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into user
                        (email, password, name, gender)
                        values
                        (%s, %s, %s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (data['email'], hashed_password, 
                        data['name'], data['gender'])
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

            # DB에 저장된 유저의 아이디를 가져온다.
            user_id = cursor.lastrowid

            print(user_id)

        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : '이미 존재하는 회원입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        # 7. JWT 토큰을 발행한다.
        ### DB 에 저장된 유저 아이디값으로 토큰을 발행한다!
        
        access_token = create_access_token(user_id)

        # 8. 모든것이 정상이면, 회원가입 잘 되었다고 응답한다.
        return {'result' : '회원가입이 잘 되었습니다.', 
                'access_token' : access_token}