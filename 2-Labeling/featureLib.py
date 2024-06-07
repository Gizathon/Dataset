from decimal import Decimal
from math import sqrt

def get_initial_Liquidity(token0_symbol,mint_data_transaction):
  if(token0_symbol == 'WETH'):
      initial_Liquidity_ETH = mint_data_transaction[0]['amount0']
      initial_Liquidity_token = mint_data_transaction[0]['amount1']
  else:
      initial_Liquidity_ETH = mint_data_transaction[0]['amount1']
      initial_Liquidity_token = mint_data_transaction[0]['amount0']

  return initial_Liquidity_ETH,initial_Liquidity_token

def get_initial_Liquidity_token(mint_data_transaction,index):
  if(index == 1):
    return Decimal(mint_data_transaction[0]['amount1'])
  else:
    return Decimal(mint_data_transaction[0]['amount0'])

def get_mint_mean_period(mint_data_transaction,initial_timestamp):
    count = len(mint_data_transaction)
    if(count == 0):
      return 0
    mint_time_add = 0
    for transaction in mint_data_transaction:
      mint_time_add = mint_time_add + int(transaction['timestamp']) - initial_timestamp
    return mint_time_add / count

def get_swap_mean_period(swap_data_transaction,initial_timestamp):
    count = len(swap_data_transaction)
    if(count == 0):
      return 0
    swap_time_add = 0
    for transaction in swap_data_transaction:
      swap_time_add = swap_time_add +  int(transaction['timestamp']) - initial_timestamp
    return swap_time_add / count

def get_burn_mean_period(burn_data_transaction,initial_timestamp):
    count = len(burn_data_transaction)
    if(count == 0):
      return 0
    burn_time_add = 0
    for transaction in burn_data_transaction:
      burn_time_add = burn_time_add + int(transaction['timestamp']) - initial_timestamp
    return burn_time_add / count

def swap_IO_rate(swap_data_transaction,index):
  swapIn = 0
  swapOut = 0
  if(index == 1): 
    for data in swap_data_transaction:
      if(data['amount0In'] == '0'): 
        swapOut = swapOut + 1
      else:   
        swapIn = swapIn + 1
  else:         
    for data in swap_data_transaction:
      if(data['amount1In'] == '0'):
        swapOut = swapOut + 1
      else:
        swapIn = swapIn +1
  
  return swapIn,swapOut 

def get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction):
  #mint_data_transaction
  swap_len = len(swap_data_transaction)
  burn_len = len(burn_data_transaction)
  #Case 1 Swap / Burn 
  if(swap_len == 0 and burn_len == 0):
    return int(mint_data_transaction[-1]['timestamp'])
  #Case 2 Swap_transaction
  if(swap_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp']))
  #Case 3 Burn Transaction
  if(burn_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))
  #Case 4 
  return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))
  
def get_swap_amount(swap_data_transaction,j,eth_amountIn,eth_amountOut):
  if(swap_data_transaction[j][eth_amountIn] == '0'): #amountIn
    return Decimal(swap_data_transaction[j][eth_amountOut]) * (-1)
  else:
    return Decimal(swap_data_transaction[j][eth_amountIn])

def get_swap_token(swap_data_transaction,j,index):
  if(index == 1):
    swap_amount = Decimal(swap_data_transaction[j]['amount1In'])
    swap_amount = Decimal(swap_amount) - Decimal(swap_data_transaction[j]['amount1Out'])
  else:
    swap_amount = Decimal(swap_data_transaction[j]['amount0In'])
    swap_amount = Decimal(swap_amount) - Decimal(swap_data_transaction[j]['amount0Out'])

  return swap_amount  

def get_timestamp(data_transaction,index):
  try:
    return data_transaction[index]['timestamp']
  except:
    return '99999999999'

def check_rugpull(before_transaction_Eth, current_Eth):
  if ( abs(Decimal(current_Eth) / Decimal(before_transaction_Eth)) <= 0.01 ):
    if( Decimal(before_transaction_Eth) < 0 or Decimal(current_Eth) < 0): 
      return False
    else:
      return True
  else:
    return False

def is_MEV(initial_Liquidity_token, swapIn_token):
  if(swapIn_token > initial_Liquidity_token * 5): 
    return False    
  else:
    return True     

def get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,index):
    if(index == 1):
      eth_amount = 'amount0'
      eth_amountIn = 'amount0In'
      eth_amountOut = 'amount0Out'
    else:
      eth_amount = 'amount1'
      eth_amountIn = 'amount1In'
      eth_amountOut = 'amount1Out'
    
    
    swap_count = len(swap_data_transaction)
    burn_count = len(burn_data_transaction)

    
    
    current_Liquidity_Eth = Decimal(mint_data_transaction[0][eth_amount]) 
    initial_Liquidity_token = get_initial_Liquidity_token(mint_data_transaction,index)
    i,j,k = 1,0,0   
    
    while True:
      try:  
        next_timestamp = min(get_timestamp(mint_data_transaction,i),get_timestamp(burn_data_transaction,k))
        
        while(get_timestamp(swap_data_transaction,j) <= next_timestamp ):
          if(get_timestamp(swap_data_transaction,j) == '99999999999'):
            break

          #swap
          before_transaction_Eth = current_Liquidity_Eth
          current_Liquidity_Eth = current_Liquidity_Eth + get_swap_amount(swap_data_transaction,j,eth_amountIn,eth_amountOut)
          #print("swap {before : %s swap_amount : %s"%(str(before_transaction_Eth),str(current_Liquidity_Eth-before_transaction_Eth)))

          if( check_rugpull(before_transaction_Eth,current_Liquidity_Eth) ):  
              if( is_MEV(initial_Liquidity_token,get_swap_token(swap_data_transaction,j,index)) == False ):  
                print("swap rugpull : initial token = %s / before Eth = %s / after Eth = %s swapIn_token_amount = %s"%(initial_Liquidity_token,str(before_transaction_Eth),str(current_Liquidity_Eth),get_swap_token(swap_data_transaction,j,index)))
                return get_timestamp(swap_data_transaction,j), Decimal(current_Liquidity_Eth / before_transaction_Eth) -1, True, before_transaction_Eth,current_Liquidity_Eth,'swap'      
          j = j+1

        #mint 
        if(next_timestamp == get_timestamp(mint_data_transaction,i)): 
          if(next_timestamp == '99999999999'):  
            try:
                
                #Case 1 Swap/Burn
                if(swap_count == 0 and burn_count == 0):
                    return mint_data_transaction[-1]['timestamp'],0, False, 0,0,''
                #Case 2 Swap
                if(swap_count == 0):
                    return max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp']),0,False, 0,0,''
                #Case 3 Burn
                if(burn_count == 0):
                    return max(mint_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']),0,False, 0,0,''
                #Case 4 Mint/Swap/Burn
                return max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']),0,False, 0,0,''
            except:
              return 'Error occur',100.0,False,1,1
          before_transaction_Eth = current_Liquidity_Eth
          current_Liquidity_Eth = current_Liquidity_Eth + Decimal(mint_data_transaction[i][eth_amount])
          #print("mint {before : %s burn_amount : %s"%(str(before_transaction_Eth),str(current_Liquidity_Eth-before_transaction_Eth))) 
          i = i+1

        #burn 
        else:
          before_transaction_Eth = current_Liquidity_Eth
          current_Liquidity_Eth = current_Liquidity_Eth - Decimal(burn_data_transaction[k][eth_amount])
          #print("burn {before : %s burn_amount : %s"%(str(before_transaction_Eth),str(current_Liquidity_Eth-before_transaction_Eth)))
          if(check_rugpull(before_transaction_Eth,current_Liquidity_Eth)):
            return get_timestamp(burn_data_transaction,k), Decimal(current_Liquidity_Eth / before_transaction_Eth) -1, True, before_transaction_Eth,current_Liquidity_Eth,'burn'
          k = k+1
      except Exception as e:
        print(e)
        print('Critical Error Occur')
        return '1',0,False,1,1,'Error'


def token_index(data):
    if(data['token0.name'] == 'Wrapped Ether'):
        return 1
    else:
        return 0


def calc_LP_distribution(holders):
    count = 0
    for holder in holders:
        if(holder['share'] < 0.01 ):
            break
        count = count +1

    LP_avg = 100 / count
    var = 0
    for i in range(count):
        var = var + (holders[i]['share'] - LP_avg) ** 2
    
    LP_stdev = sqrt(var)

    return LP_avg,LP_stdev



Locker_address = [
'0x663a5c229c09b049e36dcc11a9b0d4a8eb9db214',   #locker
'0xe2fe530c047f2d85298b07d9333c05737f1435fb',   #locker
'0x000000000000000000000000000000000000dead' ]


def get_Lock_ratio(holders):
    for holder in holders:
        if(holder['address'] in Locker_address):
          return holder['share']
    return 0    


Burn_address = [
  '0x0000000000000000000000000000000000000000',
  '0x0000000000000000000000000000000000000001',
  '0x0000000000000000000000000000000000000002',
  '0x0000000000000000000000000000000000000003',
  '0x0000000000000000000000000000000000000004',
  '0x0000000000000000000000000000000000000005',
  '0x0000000000000000000000000000000000000006',
  '0x0000000000000000000000000000000000000007',
  '0x0000000000000000000000000000000000000008',
  '0x0000000000000000000000000000000000000009',
  '0x000000000000000000000000000000000000000a',
  '0x000000000000000000000000000000000000000b',
  '0x000000000000000000000000000000000000000c',
  '0x000000000000000000000000000000000000000d',
  '0x000000000000000000000000000000000000000e',
  '0x000000000000000000000000000000000000000f',
  '0x000000000000000000000000000000000000dead',
  '0x000000000000000000000000000000000000DEAD'
]


def get_burn_ratio(holders):
  for holder in holders:
    if(holder['address'] in Burn_address):
      return holder['share']
    
  return 0


def get_creator_ratio(holders,creator_address):
  for holder in holders:
    if(holder['address'] == creator_address):
      return holder['share']
  
  return 0


