import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os


class portfolio:
    
    def __init__(self, assets, descrip, positions):
        self.assets = assets
        self.descrip = descrip
        self.postions = positions
        
    def portfolio_metrics(self):
        self.cagr = 0
        self.vol = 0
        self.sharpe = 0
        self.maxdd
    
    def calculate_rets(self):
        '''calculate portfolio returns based on positions'''
        

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
    
def Trend_Strategy(Prices):
    '''Determine postions based on trends of assets. If price is above 200 day SMA then long else no position'''
    rolling_window = 200
    positions = pd.DataFrame(columns = Prices.columns)
    
    SMA = Prices.rolling(window=rolling_window).mean()
    
    #plot SMA
    ax = Prices.plot()
    SMA.plot(ax=ax)
    plt.show()
    
    #determine positions
    for day in SMA.index:
        for asset in SMA.columns:
            if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                positions.loc[day,asset] = 1
            else:
                positions.loc[day,asset] = 0
    
    return positions.shift(1).dropna(how='all')
    
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
    
    ############################################################################
    ############################## Plotting Tests ##############################
    ############################################################################
    
    #basic plot test
    #Prices.plot()
    #plt.xlabel('Date')
    #plt.ylabel('Price')
    #plt.title('Price Chart')
    #plt.tight_layout()
    #plt.show()    
    
    ##plot test with secondary axis
    #fig, ax1 = plt.subplots()
    #ax2 = ax1.twinx()
    #ax1.plot(Prices.index, Prices.SPX, 'g-')
    #ax2.plot(Prices.index, Prices.SPY, 'b-')
    #ax1.set_xlabel('Date')
    #ax1.set_ylabel('SPX data')
    #ax2.set_ylabel('SPY data')
    #plt.show()
    
    #plot cumulative returns
    startdate = datetime(2016,1,1)
    enddate = datetime.now()
    overlapping_rets = Returns[(Returns.index>=startdate) & (Returns.index<=enddate)]  
    overlapping_rets.dropna(how='any',inplace=True)
    Cumul_Returns = (1+overlapping_rets).cumprod()-1
    ax = Cumul_Returns.plot()
    plt.xlabel('Date')
    plt.ylabel('Return (%)')
    plt.title('Cumulative Returns')  
    #format y-axis as percentage
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])          
    plt.tight_layout()
    plt.show()    
    
    
    ############################################################################
    
    
    #testing trend following strategy
    trend_following_pos  = Trend_Strategy(Prices[['SPY']])
    
    #initialize a portfolio
    test_port1 = portfolio(['SPY'],"Trend following test porfolio",trend_following_pos)
    print("Done!")