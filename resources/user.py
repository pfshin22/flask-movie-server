from flask import request
from flask.json import jsonify
from flask_jwt_extended.utils import get_jwt_identity
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended.view_decorators import jwt_required


class UserInfoResource(Resource) :
    @jwt_required()
    def get(self) :
        
        user_id = get_jwt_identity()

        # 이 유저아이디가 있어야, db에 select 할수 있다.

        # 2. DB에서 이메일로 해당 유저의 정보를 받아온다.
         
        try :
            connection = get_connection()

            query = '''select id, email, name, gender 
                        from user
                        where id = %s; '''
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            # i = 0
            # for record in record_list:
            #     record_list[i]['created_at'] = str(record['created_at'])
            #     i = i + 1

            # 우리 화면의 상단의 유저 정보 부분의 데이터
            user_info = record_list[0]

            # 우리 화면의 하단에 있는, 내 리뷰만 가져오는 데이터는
            # 커넥션 끊지 않고 여기서 바로 다시 쿼리문 만들어서
            # 사용한다.

            query = '''select r.id, m.title, r.rating 
                    from rating r
                    join movie m
                    on r.user_id = %s and r.movie_id = m.id;'''
            
            param = (user_id, )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()

            review_list = record_list

            
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
        
        
        return {"user_info" : user_info, 
                "review_list" : review_list}