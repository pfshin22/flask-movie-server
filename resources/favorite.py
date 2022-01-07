from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

class FavoriteResource(Resource) :
    @jwt_required()
    def post(self, movie_id) :

        user_id = get_jwt_identity()

        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into favorite
                        (movie_id, user_id)
                        values
                        (%s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (movie_id, user_id)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()


        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : '이미 이 영화는 즐겨찾기 했습니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')        

        return {'result' : '즐겨찾기 되었다.'}

    @jwt_required()
    def delete(self, movie_id) :

        user_id = get_jwt_identity()

        try :
            # 1. DB 에 연결
            connection = get_connection()
            
            # 2. 쿼리문 만들고
            query = '''delete from favorite
                        where movie_id = %s and user_id= %s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (movie_id, user_id)
            
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
        return {'result' : '즐겨찾기 해제 되었습니다.'}, HTTPStatus.OK

class FavoriteListResource(Resource) :
    @jwt_required()
    def get(self) :
        # 클라이언트가 준 정보를 받아온다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()

        # 영화이름, 리뷰갯수, 리뷰평점 가져오기
        try :
            connection = get_connection()

            query = '''select f.id as favorite_id, f.movie_id, f.user_id,
                        m.title, count(r.rating) as cnt, 
                        avg(r.rating) as avg
                        from favorite f
                        join movie m
                        on f.user_id = %s and f.movie_id = m.id
                        join rating r
                        on f.movie_id = r.movie_id
                        group by f.movie_id
                        order by f.created_at desc
                        limit ''' + offset + ',' + limit + ''';'''
            
            params = (user_id, )
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, params)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['avg'] = str(record['avg'])
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

        return {  "count" : len(record_list) , 
                    "favorite_list" : record_list}