from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from email_validator import validate_email, EmailNotValidError

from utils import hash_password, check_password

from flask_jwt_extended import create_access_token

class UserLoginResource(Resource) :
    def post(self) : 

        data = request.get_json()
        # email, password

        # 2. DB에서 이메일로 해당 유저의 정보를 받아온다.
         
        try :
            connection = get_connection()

            query = '''select * 
                        from user
                        where email = %s; '''
            
            param = (data['email'], )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = str(record['created_at'])
                i = i + 1
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')

        # 2-1. 만약 없는 이메일 주소로 DB에 요청했을땐
        #      데이터가 없으므로, 클라이언트에게 
        #      회원가입 되어있지 않다고, 응답한다.
        if len( record_list ) == 0 :
            return {'error' : '회원가입 되어있지 않은 사람입니다.'}, HTTPStatus.BAD_REQUEST

        # 3. 클라이언트로부터 받은 비번과, DB에 저장된 비번이
        #    동일한지 체크한다.        
        # data['password']
        # record_list[0]['password']        
        if check_password(data['password'], record_list[0]['password']) == False :
            # 4. 다르면, 비번 틀렸다고 클라이언트에 응답한다.
            return {'error' : '비번이 다릅니다.'}, HTTPStatus.BAD_REQUEST

        # 5. JTW 인증 토큰을 만들어준다.
        #    유저 아이디를 가지고 인증토큰을 만든다.
        user_id = record_list[0]['id']
        access_token = create_access_token(user_id)

        return {'result' : '로그인이 되었습니다.', 'access_token' : access_token}
        