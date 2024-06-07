import requests
import json
from bs4 import BeautifulSoup
import re

mint_query_template = '''
{
  mints(first: 1000, orderBy: timestamp, orderDirection: asc, where:{ pair: "%s" , timestamp_gt:%s  }) {
      amount0
      amount1
      to
      sender
      timestamp
 }
}
''' 

mint_query_first = '''
{
  mints(first: 1, orderBy: timestamp, orderDirection: asc, where:{ pair: "%s" }) {
      amount0
      amount1
      to
      sender
      timestamp
 }
}
'''


swap_query_template = '''
{
  swaps(first: 1000, orderBy: timestamp, orderDirection: asc, where:{ pair: "%s" , timestamp_gt:%s }) {
      amount0In
      amount0Out
      amount1In
      amount1Out
      to
      sender
      timestamp
 }
}
''' 


burn_query_template = '''
{
  burns(first: 1000, orderBy: timestamp, orderDirection: asc, where:{ pair: "%s" , timestamp_gt:%s }) {
      amount0
      amount1
      to
      sender
      timestamp
 }
}
''' 


def run_query(query):

    # endpoint where you are making the request
    request = requests.post('https://gateway-arbitrum.network.thegraph.com/api/829116bfdd9d51f6394344cac20289b0/subgraphs/id/A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum',
                            json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query))

def call_theGraph_mint(pair_id):
    mint_array = [] 
    timestamp = 0
    try:
      while(True):
        query = mint_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['mints']) < 1000): 
          mint_array.extend(result['data']['mints'])
          break

        mint_array.extend(result['data']['mints'])
        timestamp = result['data']['mints'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_swap')
      print(e)
      
    return mint_array

def call_theGraph_swap(pair_id):
    swap_array = [] 
    timestamp = 0
    try:
      while(True):
        query = swap_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['swaps']) < 1000): 
          swap_array.extend(result['data']['swaps'])
          break

        swap_array.extend(result['data']['swaps'])
        timestamp = result['data']['swaps'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_swap')
      print(e)
      
    return swap_array

def call_theGraph_burn(pair_id):
    burn_array = [] 
    timestamp = 0
    try:
      while(True):
        query = burn_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['burns']) < 1000): 
          burn_array.extend(result['data']['burns'])
          break

        burn_array.extend(result['data']['burns'])
        timestamp = result['data']['burns'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_burn')
      print(e)
      
    return burn_array



def get_creatorAddress(pair_id,token_id):
    repos_url = 'https://api.ethplorer.io/getAddressInfo/'+token_id+'?apiKey=EK-4L18F-Y2jC1b7-9qC3N'
    response = requests.get(repos_url).text
    repos = json.loads(response)    
    
    try:
        creator_address = repos['contractInfo']['creatorAddress']
        if(creator_address == None):
          raise ValueError
    except:     
         url = 'https://etherscan.io/address/'+token_id
         try:
             response = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'})
             page_soup = BeautifulSoup(response.text, "html.parser")
             Transfers_info_table_1 = str(page_soup.find("a", {"class": "hash-tag text-truncate"}))
             creator_address = re.sub('<.+?>', '', Transfers_info_table_1, 0).strip()
             if(creator_address == 'None'):
                query = mint_query_first % pair_id
                response = run_query(query)
                creator_address = response['data']['mints'][0]['to']
         except Exception as e:  
              print(e)
              creator_address = 'Fail to get Creator Address'
    
    # if creator_address in proxy_contracts:
    #     query = mint_query_first % pair_id
    #     response = run_query(query)
    #     creator_address = response['data']['mints'][0]['to']
    
    return creator_address

def get_holders(token_id):
    repos_url = 'https://api.ethplorer.io/getTopTokenHolders/'+token_id+'?apiKey=EK-4L18F-Y2jC1b7-9qC3N&limit=100'
    response = requests.get(repos_url)
    if(response.status_code == 400):
        return []
    repos = json.loads(response.text)    
    return repos['holders']