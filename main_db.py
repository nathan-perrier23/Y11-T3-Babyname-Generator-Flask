import sqlite3
from sqlite3 import Error
import sys, os

class DATA:
    def __init__(self):
        pass
        
    
    def main_db(self, table, db):
        
        conn_db = self.create_db_connection(db)
        
        # create tables
        if conn_db is not None:
            self.create_table(table,conn_db)
            
            # print('placement - Username - score')
            # print(conn_db.execute("select * from high_scores").fetchall())
            
            conn_db.close()
      
        else:
            print("Error! cannot create the database connection.")
    
    
    
    def create_table(self, create_table_sql, conn_db):
        try:
            c = conn_db.cursor()
            c.execute(create_table_sql)
            conn_db.commit()
            print('tables created')
        except Error as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    
    def create_db_connection(self,db_file):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            return sqlite3.connect(db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
                
    def get_contents(self, item, table, db):
        conn_db = self.create_db_connection(db)
        if conn_db is not None:
            cursor = conn_db.execute('''select * from sqlite_master''')
            request = "SELECT " + str(item) + " FROM " + str(table)
            return [item1[0] for item1 in cursor.execute(request)]
        else:
            print("Error! cannot create the database connection.")
        conn_db.close()
        
    #TODO def insert_contents(self, item, table, db):