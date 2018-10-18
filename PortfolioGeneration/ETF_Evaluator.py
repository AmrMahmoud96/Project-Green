#Used to compare and evaluate ETFs with respect to chosen indicies

#imports
import pandas as pd
import numpy as np
import os 

def plot(index, etfs):
    return

def load_data(fname, Prices):
    '''load in historical prices'''
    ticker = fname[0:-4]
    data = pd.read_csv("Data/ETF/" + fname)
    data.set_index('Date', inplace=True)
    data = data[["Adj Close"]]
    data.columns = [ticker]
    data.index = pd.to_datetime(data.index)
    first_day = data.first_valid_index()
    last_day = data.index.values[-1]
    num_days = len(data)
    Info.loc['First Day',ticker] = first_day
    Info.loc['Last Day',ticker] = last_day
    Info.loc['Num of Days',ticker] = num_days
    Info.loc['Proxy',ticker] = 'test'
    Prices = pd.concat([Prices, data], axis=1, sort=True)
    return Prices

if __name__ == "__main__":
    print("Started...")
    #load prices and calculate returns
    Prices = pd.DataFrame()
    Info = pd.DataFrame()
    for fname in os.listdir("Data/ETF"):
        Prices = load_data(fname,Prices)
    
    Returns = Prices.pct_change() 
    print("Prices and returns loaded!")    
    
    #save output
    Info.to_csv('Info.csv')
    
    
    print("Done!")