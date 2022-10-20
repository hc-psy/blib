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
