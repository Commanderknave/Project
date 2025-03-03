import pymysql
import pymysql.cursors
import DB_CONFIG

def db_access(sqlProc, sqlArgs):
    try:
        dbConnection = pymysql.connect(
            host=DB_CONFIG.DB_HOST,
            user=DB_CONFIG.DB_USER,
            password=DB_CONFIG.DB_PASSWORD,
            database=DB_CONFIG.DB_DATABASE,
            cursorclass= pymysql.cursors.DictCursor)
        cursor = dbConnection.cursor()
        cursor.callproc(sqlProc, sqlArgs)
        affected_count=cursor.rowcount
        rows = cursor.fetchall()
        dbConnection.commit()
        cursor.close()
    except pymysql.MySQLError as e:
        raise Exception('Database Error:'+str(e))
    finally:
        dbConnection.commit()
        dbConnection.close()
    return rows,affected_count

def get_cursor():
    try:
        dbConnection = pymysql.connect(
            host=DB_CONFIG.DB_HOST,
            user=DB_CONFIG.DB_USER,
            password=DB_CONFIG.DB_PASSWORD,
            database=DB_CONFIG.DB_DATABASE,
            cursorclass= pymysql.cursors.DictCursor)
        return dbConnection.cursor()
    except pymysql.MySQLError as e:
        raise Exception('Database Error:'+str(e))
    finally:
        dbConnection.commit()
        dbConnection.close()
        