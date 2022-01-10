from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd 

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



class MovieRecommResource(Resource):
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        # 상관계수 데이터프레임을 읽어온다.
        df = pd.read_csv('data/movie_correlations.csv', index_col='title')

        # 이 유저의 별점 정보를 가져온다. DB에서
        try :
            connection = get_connection()

            query = '''select r.id, r.user_id, r.movie_id, 
                        r.rating, m.title 
                        from rating r
                        join movie m
                        on r.user_id = %s and r.movie_id = m.id;'''
            
            params = (user_id, )
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, params)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            # i = 0
            # for record in record_list:
            #     record_list[i]['avg'] = str(record['avg'])
            #     i = i + 1
            
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


        # 유저의 정보를 pandas dataframe으로 만들어준다.
        my_rating = pd.DataFrame(data=record_list)

        print(my_rating)

        # # 모든 영화에 대한 가중치 계산하는 코드
        similar_movies_list = pd.DataFrame()

        for i in range( len(my_rating) ) :
            similar_movie = df[my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = my_rating['rating'][i] * similar_movie['Correlation']
            similar_movies_list = similar_movies_list.append(similar_movie)

        similar_movies_list.reset_index(inplace=True)

        # 영화 제목이 중복된 것은, 해당영화의 웨이트가 최대인것으로 선택한다.
        similar_movies_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 유저가 본 영화제목은 여기서 제외해야 한다. 따라서 먼저, 타이틀을 인덱스가 아니, 컬럼으로 올린다.
        similar_movies_list = similar_movies_list.reset_index()

        # # 이미 유저가 봐서 별점 준 영화는, 위의 추천 리스트에서 제거해야 한다.
        # # 따라서, 유저가 본 영화 제목만 따로 가져온다.
        title_list = my_rating['title'].tolist()

        # # 있는것들만 체크 : isin 함수이고
        # # 있는것은 제외하는 것은 :  isin 함수 적용한것의 맨 왼쪽에 ~ 표시를 붙여준다.
        recomm_movies_list = similar_movies_list.loc[ ~similar_movies_list['title'].isin( title_list )  , ].head(10)

        print(recomm_movies_list)

        # # 위의 결과를 JSON으로 바꿔서 클라이언트에게 응답!
        # # 이런 모양의 json으로 만들어서 보냅니다.
        # # [ {'title':'Mikey and Nicky', 'Weight':3.225284} , 
        # # {'title':'Love Hina Spring Special', 'Weight':3.047558 },
        # # ]
        # recomm_movies_list.to_dict('records')
        # print(recomm_movies_list)
        return {'movie_list' : recomm_movies_list.to_dict('records')}

class MovieRealtimeRecommResource(Resource):
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        # 이 유저의 별점 정보를 가져온다. DB에서
        try :
            connection = get_connection()

            # 실시간으로 상관계수를 측정하기 위해, 
            # 먼저 테이블로부터 정보를 가져온다.
            query = '''select user_id, movie_id, rating, title 
                        from rating r
                        join movie m
                        on r.movie_id = m.id;'''

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query)
            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()

            movies_rating_df = pd.DataFrame(data=record_list)
            userid_movietitle_matrix = movies_rating_df.pivot_table(index= 'user_id', columns='title', values='rating')
            # 영화별로 50개 이상의 리뷰가 있는 영화만 상관계수를 뽑으라는 뜻.
            df = userid_movietitle_matrix.corr(min_periods=50)


            query = '''select r.id, r.user_id, r.movie_id, 
                        r.rating, m.title 
                        from rating r
                        join movie m
                        on r.user_id = %s and r.movie_id = m.id;'''
            
            params = (user_id, )
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, params)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            # i = 0
            # for record in record_list:
            #     record_list[i]['avg'] = str(record['avg'])
            #     i = i + 1
            
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


        # 유저의 정보를 pandas dataframe으로 만들어준다.
        my_rating = pd.DataFrame(data=record_list)

        print(my_rating)

        # # 모든 영화에 대한 가중치 계산하는 코드
        similar_movies_list = pd.DataFrame()

        for i in range( len(my_rating) ) :
            similar_movie = df[my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlation']
            similar_movie['Weight'] = my_rating['rating'][i] * similar_movie['Correlation']
            similar_movies_list = similar_movies_list.append(similar_movie)

        similar_movies_list.reset_index(inplace=True)

        # 영화 제목이 중복된 것은, 해당영화의 웨이트가 최대인것으로 선택한다.
        similar_movies_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 유저가 본 영화제목은 여기서 제외해야 한다. 따라서 먼저, 타이틀을 인덱스가 아니, 컬럼으로 올린다.
        similar_movies_list = similar_movies_list.reset_index()

        # # 이미 유저가 봐서 별점 준 영화는, 위의 추천 리스트에서 제거해야 한다.
        # # 따라서, 유저가 본 영화 제목만 따로 가져온다.
        title_list = my_rating['title'].tolist()

        # # 있는것들만 체크 : isin 함수이고
        # # 있는것은 제외하는 것은 :  isin 함수 적용한것의 맨 왼쪽에 ~ 표시를 붙여준다.
        recomm_movies_list = similar_movies_list.loc[ ~similar_movies_list['title'].isin( title_list )  , ].head(10)

        print(recomm_movies_list)

        # # 위의 결과를 JSON으로 바꿔서 클라이언트에게 응답!
        # # 이런 모양의 json으로 만들어서 보냅니다.
        # # [ {'title':'Mikey and Nicky', 'Weight':3.225284} , 
        # # {'title':'Love Hina Spring Special', 'Weight':3.047558 },
        # # ]

        # recomm_movies_list.to_dict('records')
        
        return {'movie_list' : recomm_movies_list.to_dict('records')}