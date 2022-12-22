#methods to query database using connection cursor
from django.db import connection


class SingleCursor:
    "fetches a single row from the database with column names"
    def __init__(self) -> None:
        pass

    @staticmethod
    def send_query(query_string):
        "process the query string"
        try:
            #with connection.cursor() as cursor:
            cursor = connection.cursor()
            cursor.execute(query_string)
            row = cursor.fetchone()
            col_names = [desc[0] for desc in cursor.description]
            row_dict = dict(zip(col_names, row))
            cursor.close()
            return row_dict
        except Exception as e:
            print(e)
            return str(e)
        finally:
            if connection:
                connection.close()          

class MultipleCursor:
    "fetches multiple rows from the database with column names"
    def __init__(self) -> None:
        pass

    @staticmethod
    def send_query(query_string, rows=None):
        "process the query string"
        try:
            cursor = connection.cursor()
            cursor.execute(query_string)
            if rows is None:
                rows = 150 #number of rows to be retrieved
            results = cursor.fetchmany(rows)
            row_dict_list = [dict(zip([col[0] for col in cursor.description], row)) for row in results]
            cursor.close()
            return row_dict_list
        except Exception as e:
            print(e)
            return str(e)
        finally:
            if connection:
                connection.close()    


class DBIDGENERATOR:
    "to generate unique ID that can be used in a table as record ID(primary key) using Oracle Sequence method"

    @staticmethod
    def process_id(sequence):
        "get next value from Oracle Sequence object, here dual refers to system table"
        from functions.kwlogging import SimpleLogger
        query = f"select {sequence}.NEXTVAL from dual"
        res = SingleCursor.send_query(query)
        if type(res) is str: #if query fails, create a new sequence
            query = f"CREATE SEQUENCE {sequence} START WITH 1000 INCREMENT BY 1 NOCACHE NOCYCLE;"
            SingleCursor.send_query(query)
            SimpleLogger.do_log(f"New sequence created: {sequence}")
            return 1000
        else:
            nextVal = res['NEXTVAL']
            SimpleLogger.do_log(f"nextVal: {nextVal}")
            return nextVal

    @staticmethod
    def process_gid(prefix):
        "to generate an unique ID based on Oracle Sequence and a prefix"
        from functions.kwlogging import SimpleLogger
        sequence = 'KW_GID'
        query = f"select {sequence}.NEXTVAL from dual"
        res = SingleCursor.send_query(query)
        if type(res) is str: #if query fails, create a new sequence
            query = f"CREATE SEQUENCE {sequence} START WITH 1000 INCREMENT BY 1 NOCACHE NOCYCLE;"
            SingleCursor.send_query(query)
            SimpleLogger.do_log(f"New sequence created: {sequence}")
            return prefix + str(1000)
        else:
            nextVal = res['NEXTVAL']
            SimpleLogger.do_log(f"nextVal: {nextVal}")
            return prefix + str(nextVal)
                

       
            

