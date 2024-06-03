from pprint import pprint
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import pandas as pd
import json
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import requests
import time

# swap function makes scam token to token0
def switch_token(result):
    if 'data' not in result or 'pairs' not in result['data']:
        print("Invalid result structure:", result)
        return
    for pair in result['data']['pairs']:
        if (int(pair['token0']['txCount']) > int(pair['token1']['txCount'])):
            pair['reserve00'], pair['reserve11'] = pair['reserve1'], pair['reserve0']
            pair['token00'], pair['token11'] = pair['token1'], pair['token0']
        else:
            pair['reserve00'], pair['reserve11'] = pair['reserve0'], pair['reserve1']
            pair['token00'], pair['token11'] = pair['token0'], pair['token1']

# function to use requests.post to make an API call to the subgraph url
def run_query(query):
    # endpoint where you are making the request
    request = requests.post('https://gateway-arbitrum.network.thegraph.com/api/30f67c1ef7d30ea143e6aab98a97703b/subgraphs/id/A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum',
                            json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}. {}'.format(request.status_code, query))


query_init = '''
{
 pairs(first: 1000, orderBy: createdAtBlockNumber, orderDirection: desc) {
   id
   token0{
    id
    symbol
    name
    txCount
    totalLiquidity
  }
   token1{
    id
    symbol
    name
    txCount
    totalLiquidity
  }
   reserve0
   reserve1
   totalSupply
   reserveUSD
   reserveETH
   txCount
   createdAtTimestamp
   createdAtBlockNumber
 }
}
'''


query_iter_template = '''
{
 pairs(first: 1000, orderBy: createdAtBlockNumber, orderDirection: desc, where: {createdAtBlockNumber_lt:initial}) {
   id
   token0{
    id
    symbol
    name
    txCount
    totalLiquidity
  }
   token1{
    id
    symbol
    name
    txCount
    totalLiquidity
  }
   reserve0
   reserve1
   totalSupply
   reserveUSD
   reserveETH
   txCount
   createdAtTimestamp
   createdAtBlockNumber
 }
}
'''

pair_frame = []  # List to store query results

# First query
query = query_init
result = run_query(query)
print("Initial query result:")
pprint(result)
switch_token(result)
if 'data' in result and 'pairs' in result['data']:
    for pair in result['data']['pairs']:
        if ((pair['token0']['symbol'] != 'WETH') & (pair['token1']['symbol'] != 'WETH')):
            continue
        year = time.gmtime(int(pair['createdAtTimestamp'])).tm_year
        month = time.gmtime(int(pair['createdAtTimestamp'])).tm_mon
        day = time.gmtime(int(pair['createdAtTimestamp'])).tm_mday
        pair['createdAtTimestamp'] = str(year) + '-' + str(month) + '-' + str(day)
        pair_frame.append(pair)

    last_block = result['data']['pairs'][-1]['createdAtBlockNumber']
    query_iter = query_iter_template.replace('initial', last_block)

    try:
        while True:
            result = run_query(query_iter)
            print("Iterative query result:")
            pprint(result)
            switch_token(result)
            if 'data' not in result or 'pairs' not in result['data']:
                print("Invalid result structure during iteration:", result)
                break
            for pair in result['data']['pairs']:
                if ((pair['token0']['symbol'] != 'WETH') & (pair['token1']['symbol'] != 'WETH')):
                    continue
                year = time.gmtime(int(pair['createdAtTimestamp'])).tm_year
                month = time.gmtime(int(pair['createdAtTimestamp'])).tm_mon
                day = time.gmtime(int(pair['createdAtTimestamp'])).tm_mday
                pair['createdAtTimestamp'] = str(year) + '-' + str(month) + '-' + str(day)
                pair_frame.append(pair)
            last_block = result['data']['pairs'][-1]['createdAtBlockNumber']
            query_iter = query_iter_template.replace('initial', last_block)

    except Exception as e:
        try:
            print(result['errors'])
        except:
            print(e)
        df = pd.json_normalize(pair_frame)
        df.to_csv('main_pair.csv', encoding='utf-8-sig', index=False)
else:
    print("Initial query returned no data or pairs:", result)
