import pymysql
import config


def get_connection():

    print("HOST:", config.DB_HOST)
    print("PORT:", config.DB_PORT)
    print("USER:", config.DB_USER)
    print("DATABASE:", config.DB_NAME)

    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )