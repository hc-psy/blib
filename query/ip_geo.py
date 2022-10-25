import requests
import json
import pandas as pd
from dbcnnct import db_connect
from config import INFO
from tqdm.auto import tqdm
import csv
import argparse


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
    
    # fetch result dataframe
    try:
        result_df = pd.read_csv(result_fn)
    except:
        headers=['ip', 'lat', 'lon', 'city', 'country', 'continent']
        
        with open(result_fn, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        result_df = pd.read_csv(result_fn)
    
    # diff set of ip_df and result_df
    result_df_ip = result_df[["ip"]]
    remain_ip_df = pd.concat([ip_df, result_df_ip, result_df_ip]).drop_duplicates(keep=False)
    
    # to numpy and iterate
    dfnum = remain_ip_df.to_numpy()
    with open(result_fn, 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        
        for ip in tqdm(dfnum):
            row = geo2latlon(ip[0])
            writer.writerow([ip[0], *row])


def fetch_distinct_ip_and_save(filename):
    
    # fetch ip csv
    try:
        df = pd.read_csv(filename)
    except:
        cnxn, _ = db_connect()
        query = f"SELECT DISTINCT ip FROM {INFO['table'][1]}"
        df = pd.read_sql(query, cnxn)
        df.to_csv(filename, index=False)
    
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create IP GEO MAP')
    parser.add_argument('--ip_fn')
    parser.add_argument('--result_fn')
    args = parser.parse_args()
    
    ip_fn = args.ip_fn
    result_fn = args.result_fn
    
    ip_df = fetch_distinct_ip_and_save(ip_fn)
    create_geo_info(ip_df, result_fn)