from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

class MovieListResource(Resource) :
    def get(self) :
        # 1. 쿼리 스트링의 정보를 가져오기. 두가지 방법
        # 키, 밸류로 가져오는 방법
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        order = request.args.get('order')

        # 딕셔너리로 전부 받아서 가져오는 방법
        # query_params = request.args.to_dict()
        # query_params['offset']

        # 2. 디비에 쿼리 한다.
        try :
            connection = get_connection()

            if order == 'count' :
                query = '''select m.id, m.title, count(r.rating) as cnt, avg(r.rating) as avg
                            from movie m
                            join rating r
                            on m.id = r.movie_id
                            group by m.title
                            order by cnt desc
                            limit ''' + offset + ','+limit+''';'''
            
            elif order == 'average' :
                query = '''select m.id, m.title, count(r.rating) as cnt, avg(r.rating) as avg
                            from movie m
                            join rating r
                            on m.id = r.movie_id
                            group by m.title
                            order by avg desc
                            limit ''' + offset + ','+limit+''';'''                
            
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query)

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
                "movie_list" : record_list}


class MovieSearchResource(Resource) :
    def get(self) :
        # 1. 쿼리 스트링의 정보를 가져오기. 두가지 방법
        # 키, 밸류로 가져오는 방법
        # offset = request.args.get('offset')
        # limit = request.args.get('limit')
        # keyword = request.args.get('keyword')

        # 딕셔너리로 전부 받아서 가져오는 방법
        query_params = request.args.to_dict()
        # query_params['offset']
        # ?offset=0&limit=25&keyword=hi

        # 2. 디비에 쿼리 한다.
        try :
            connection = get_connection()

            
            query = '''select m.id, m.title, count(r.rating) as cnt, avg(r.rating) as avg
                        from movie m
                        join rating r
                        on m.id = r.movie_id
                        where m.title like '%'''+query_params['keyword']+'''%'
                        group by m.title
                        order by cnt desc
                        limit ''' + query_params['offset'] + ','+query_params['limit']+''';'''
        
                
        
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query)

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
                "movie_list" : record_list}