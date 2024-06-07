from pandas.core.frame import DataFrame
import pandas as pd
import time
from tqdm import tqdm
from multiprocessing import Pool
from multiprocessing import Process
from mylib import *
from TheGraphLib import *
from featureLib import *
import datetime

def switch_file(file_name):
    global datas
    datas = pd.read_csv(file_name).to_dict('records')

def get_feature(data):
    
    pair_address = data['id']
    token_address = data['token00.id']

    #TheGraph API
    mint_data_transaction = call_theGraph_mint(pair_address)
    swap_data_transaction = call_theGraph_swap(pair_address)
    burn_data_transaction = call_theGraph_burn(pair_address)

    #initial_Liquidity 
    initial_Liquidity_Eth , initial_Liquidity_Token = get_initial_Liquidity(data['token0.symbol'],mint_data_transaction)

    
    mint_count = len(mint_data_transaction)
    swap_count = len(swap_data_transaction)
    burn_count = len(burn_data_transaction)

    # Mint/Burn/Swap
    initial_timestamp = int(mint_data_transaction[0]['timestamp'])
    last_timestamp = get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction)
    active_period = last_timestamp - initial_timestamp
    mint_mean_period = int(get_mint_mean_period(mint_data_transaction,initial_timestamp))
    swap_mean_period = int(get_swap_mean_period(swap_data_transaction,initial_timestamp))
    burn_mean_period = int(get_burn_mean_period(burn_data_transaction,initial_timestamp))
    
    #SwapIn/SwapOut 
    swapIn,swapOut = swap_IO_rate(swap_data_transaction,token_index(data))    

    #rugpull timestamp 
    rugpull_timestamp, rugpull_change, is_rugpull, before_rugpull_Eth, after_rugpull_Eth,rugpull_method = get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,token_index(data))

    #rugpull
    rugpull_proceeding_time = int(rugpull_timestamp) - int(initial_timestamp)
    if(is_rugpull == False):
        rugpull_proceeding_time = 0
        rugpull_method = ''
        rugpull_timestamp = '0'
        rugpull_change = ''

    creater_Address = get_creatorAddress(pair_address, token_address)
    holder_Address = get_holders(token_address)
    lp_Avg, lp_Std = calc_LP_distribution(holder_Address)
    lp_lockRatio = get_Lock_ratio(holder_Address)
    creater_holdingRatio = get_creator_ratio(holder_Address, creater_Address)
    burnRatio = get_burn_ratio(holder_Address)
    initial_Liquidity_Token = float(initial_Liquidity_Token)
    fswapIn = float(swapIn)
    isMev = is_MEV(initial_Liquidity_Token, fswapIn)

    data['initial_Liquidity_Eth'] = initial_Liquidity_Eth
    data['initial_Liquidity_Token'] = initial_Liquidity_Token   
    data['last_transaction_timestamp'] = last_timestamp
    data['last_transaction_date'] = datetime.datetime.fromtimestamp(int(last_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    data['mint_count'] = mint_count
    data['swap_count'] = swap_count
    data['burn_count'] = burn_count
    data['mint_mean_period'] = mint_mean_period
    data['swap_mean_period'] = swap_mean_period
    data['burn_mean_period'] = burn_mean_period
    data['swapIn'] = swapIn
    data['swapOut'] = swapOut
    data['token_burn_ratio'] = burnRatio
    data['lp_avg'] = lp_Avg
    data['lp_std'] = lp_Std
    data['creator_holding_ratio'] = creater_holdingRatio
    data['lp_lock_ratio'] = lp_lockRatio
    data['is_MEV'] = isMev
    data['active_period'] = active_period
    data['rugpull_method'] = rugpull_method
    data['rugpull_timestamp'] = rugpull_timestamp
    data['rugpull_timestamp_date'] = datetime.datetime.fromtimestamp(int(rugpull_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    data['before_rugpull_Eth'] = before_rugpull_Eth
    data['after_rugpull_Eth'] = after_rugpull_Eth
    data['rugpull_change'] = rugpull_change 
    data['rugpull_proceeding_hour'] = str(rugpull_proceeding_time / 3600) + 'h'
    data['is_rugpull'] = is_rugpull


     
    return data



# if __name__=='__main__':
#     createFolder('./result')
#     file_name = 'zero.csv'
#     file_count = split_csv(file_name)
#     out_list = []
#     out_list = list(input('입력(공백단위) : ').split())

#     for i in out_list:         #하나의 파일 단위로 Creator Address 불러오고, 해당 초기 유동성풀 이더값 구해온다.
#         file_name = './result/out{}.csv'.format(i)
#         switch_file(file_name)
#         datas_len = len(datas)
#         try:
#             p = Pool(1)
#             count = 0
#             result = []
#             for ret in p.imap(get_feature,datas):
#                 count = count+1
#                 result.append(ret)
#                 if(count % 200 == 0):
#                     print("Process Rate : {}/{} {}%".format(count,datas_len,int((count/datas_len)*100)))
#             p.close()
#             p.join()
#         except Exception as e:
#             print(e)
#         print('===================================   finish    =========================================')
#         time.sleep(5)
            
#         df = pd.DataFrame(result)
#         file_name = './result/fout{}.csv'.format(i)
#         df.to_csv(file_name,encoding='utf-8-sig',index=False)
#         print(file_name + ' complete')
#     merge_csv()



import time
import pandas as pd
from multiprocessing import Pool
import os

if __name__=='__main__':
    createFolder('./result')
    file_name = './Splits/split_0.csv'
    file_count = split_csv(file_name)
    out_list = []
    out_list = list(input('SPLITS : ').split())

    for i in out_list:  # Process each input file
        file_name = './result/out{}.csv'.format(i)
        switch_file(file_name)
        datas_len = len(datas)
        
        num_cores = os.cpu_count
        p = Pool(8)
        count = 0
        result = []

        try:
            for data in datas:
                try:
                    ret = p.apply_async(get_feature, (data,)).get()
                    result.append(ret)
                    count += 1
                    if count % 200 == 0:
                        print("Process Rate : {}/{} {}%".format(count, datas_len, int((count/datas_len)*100)))
                except Exception as e:
                    print(f"Error processing data point: {data}, error: {e}")
            
            p.close()
            p.join()
        except Exception as e:
            print(f"Error in processing pool: {e}")
        
        print('===================================   finish    =========================================')
        time.sleep(1)
        
        df = pd.DataFrame(result)
        file_name = './result/fout{}.csv'.format(i)
        df.to_csv(file_name, encoding='utf-8-sig', index=False)
        print(file_name + ' complete')
    
    merge_csv()
