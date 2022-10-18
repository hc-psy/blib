import pyodbc
from config import INFO


def db_connect():

    cnxn_str = (f"Driver={INFO['driver']};" \
                f"Server={INFO['host'] + ',' + INFO['port']};" \
                f"Database={INFO['database']};"
                f"UID={INFO['username']};" \
                f"PWD={INFO['password']};" \
                f"Encrypt=yes;" \
                f"TrustServerCertificate=yes;")
    
    cnxn = pyodbc.connect(cnxn_str)
    crsr = cnxn.cursor()

    return cnxn, crsr


# cursor.execute(f"SELECT top 1 * FROM {INFO['table'][0]}")
# Sample select query
cursor.execute("SELECT @@version;") 
row = cursor.fetchone() 
while row: 
    print(row[0])
    row = cursor.fetchone()