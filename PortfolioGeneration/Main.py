import pandas as pd
import numpy as np
import datetime as datetime
import matplotlib.pyplot as plt
import os

def load_data(fname, Prices):
    '''load in historical prices'''
    ticker = fname[0:-4]
    data = pd.read_csv("Data/" + fname)
    data.set_index('Date', inplace=True)
    data = data[["Adj Close"]]
    data.columns = [ticker]
    data.index = pd.to_datetime(data.index)    
    Prices = pd.concat([Prices, data], axis=1, sort=True)
    return Prices
    
if __name__ == "__main__":
    print("Started...")
    #plotting styles
    plt.style.use('ggplot')
    plt.rcParams["figure.figsize"] = (12,7)    
    
    
    #load prices and calculate returns
    Prices = pd.DataFrame()
    for fname in os.listdir("Data"):
        Prices = load_data(fname,Prices)
    Returns = Prices.pct_change() 
    print("Prices and returns loaded!")
    
    #plot test
    Prices.plot()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Price Chart')
    plt.tight_layout()
    plt.show()    
    
    #plot test with secondary axis
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    ax1.plot(Prices.index, Prices.SPX, 'g-')
    ax2.plot(Prices.index, Prices.SPY, 'b-')
    
    ax1.set_xlabel('Date')
    ax1.set_ylabel('SPX data')
    ax2.set_ylabel('SPY data')
    
    #plot cumulative returns
    
    
    plt.show()    
    
    print("Done!")