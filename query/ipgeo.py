import requests
import json
import pandas as pd
from dbcnnct import db_connect
from config import INFO
from tqdm.auto import tqdm
import csv

def geo2latlon(ip_address):
    
    # URL to send the request to
    request_url = 'https://api.findip.net/' + ip_address.strip() + f'/?token={INFO["findiptoken"]}'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0", "Content-Type": "application/json"}
    
    # Send request and decode the result
    response = requests.get(request_url, headers=headers)
    result = response.content.decode()
    
    # Convert this data into a dictionary
    result  = json.loads(result)
    result = [result['location']['latitude'], result['location']['longitude'], result['city']['names']['en'], result['country']['names']['en'], result['continent']['names']['en']]

    return result


def create_geo_info(ip_df, result_fn):
    result_df = pd.read_csv(result_fn)
    result_df_ip = result_df[["ip"]]
    
    remain_ip_df = pd.concat([ip_df, result_df_ip, result_df_ip]).drop_duplicates(keep=False)
    
    headers=['ip', 'lat', 'lon', 'city', 'country', 'continent']
    
    dfnum = remain_ip_df.to_numpy()
    
    with open(result_fn, 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        # writer.writerow(headers)
        
        for ip in tqdm(dfnum):
            row = geo2latlon(ip[0])
            writer.writerow([ip[0], *row])


def fetch_distinct_ip_and_save(filename):
    try:
        df = pd.read_csv(filename)
    except:
        cnxn, _ = db_connect()
        query = f"SELECT DISTINCT ip FROM {INFO['table'][1]}"
        df = pd.read_sql(query, cnxn)
        df.to_csv(filename, index=False)
    
    return df

if __name__ == "__main__": 
    ip_fn = "./cache/ip.csv"
    ip_df = fetch_distinct_ip_and_save(ip_fn)
    result_fn = "./cache/ip2geo.csv"
    create_geo_info(ip_df, result_fn)