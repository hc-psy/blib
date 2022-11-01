import pandas as pd
from dbcnnct import db_connect
from config import INFO
import argparse


def ip_time(fn, info_value, cnxn):
    
    query = f'''
            SELECT ip, CONVERT(date, clicktime) as clickdate, COUNT(*) as count
            FROM {INFO['table'][1]}
            WHERE label_name = 'seq' 
            AND info = '{info_value}'
            AND (label_value LIKE '[0-9][0-9][0-9][0-9][0-9][0-9]')
            GROUP BY ip, CONVERT(date, clicktime);
            '''
    
    df = pd.read_sql(query, cnxn)
    df.to_csv(fn, index=False)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create COUNT')
    parser.add_argument('--is_ip', action=argparse.BooleanOptionalAction)
    parser.add_argument('--info_value', default='書目明細')
    parser.add_argument('--result_fn')
    args = parser.parse_args()
    
    
    cnxn, _ = db_connect()
    
    if args.is_ip:
        ip_time(args.result_fn, args.info_value, cnxn)