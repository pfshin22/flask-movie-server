import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'yhdbshin.cjdnoifmay48.ap-northeast-2.rds.amazonaws.com',
        database = 'movie_db',
        user = 'movie_user',
        password = '2105'
    )
    return connection

    