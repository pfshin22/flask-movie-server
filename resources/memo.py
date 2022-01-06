from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

class MemoResource(Resource) :
    @jwt_required()
    def post(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        data = request.get_json()
        # title, date, content

        # 1-1. JWT 인증토큰에서는, user_id 값을 가져온다.
        user_id = get_jwt_identity()

        # 2. DB에 메모를 저장한다.
        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into memo
                    (title, date, content, user_id)
                    values
                    (%s, %s, %s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (data['title'], data['date'],             
                    data['content'], user_id )
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')


        return {'result':'저장 완료'}, HTTPStatus.OK

    @jwt_required()
    def get(self) :

        # 1. 유저 정보를 JWT에서 가져온다.
        user_id = get_jwt_identity()

        # 2. DB에서 이 user_id 로 메모를 가져온다.

        try :
            connection = get_connection()

            query = ''' select * 
                        from memo
                        where user_id = %s ; '''
            
            cursor = connection.cursor(dictionary = True)

            param = (user_id, )
            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['date'] = str(record['date'])
                record_list[i]['created_at'] = str(record['created_at'])
                record_list[i]['updated_at'] = str(record['updated_at'])
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

        return {'data' :record_list} , HTTPStatus.OK


class MemoInfoResource(Resource) :
    @jwt_required()
    def put(self, memo_id) :
        
        # body 에 있는 json 을 받아오는 코드
        data = request.get_json()
        # title, date, content

        user_id = get_jwt_identity()

        # 메모 수정하기
        try :
            # 1. DB 에 연결
            connection = get_connection()            
            
            # 2. 쿼리문 만들고
            query = '''update memo
                        set title = %s , date = %s, 
                        content = %s
                        where id = %s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (data['title'], data['date'] , 
                        data['content'], memo_id )
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        return {'result' : '업데이트가 잘 되었습니다.'}, HTTPStatus.OK

    
    @jwt_required()
    def delete(self, memo_id) :
        
        user_id = jwt_required()

        try :
            # 1. DB 에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들고
            query = '''delete from memo
                        where id = %s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (memo_id,)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error ', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
        return {'result' : '메모 삭제가 정상적으로 동작했습니다.'}, HTTPStatus.OK