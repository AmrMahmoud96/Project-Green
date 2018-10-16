import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
import riskparity as erc_ver1


class portfolio:
    
    def __init__(self, name, descrip, positions):
        self.assets = list(positions)
        self.name = name
        self.descrip = descrip
        self.positions = positions
        self.firstday = positions.index.values[0]
        self.lastday = positions.index.values[-1]
        self.calculate_rets()
        self.portfolio_metrics()
        
    def portfolio_metrics(self):
        self.exp_ret = ((1+self.returns.mean())**252)-1
        self.vol = self.returns.std()*np.sqrt(252)
        self.sharpe = self.exp_ret/self.vol
        self.maxdd = 0
        #self.cumul_ret = 0 
    
    def calculate_rets(self):
        '''calculate portfolio returns based on positions'''
        rets = self.positions*Returns[self.assets]
        rets = rets.dropna()
        self.returns = rets.sum(axis=1)
        self.returns.name = self.name
        
    def plot_rets(self, startdate, enddate):
        '''plot cumulative returns from start to end date'''
        if not startdate:
            startdate = self.firstday
        if not enddate:
            enddate = self.lastday
            
        print('Plotting...')
        cumul_rets = (1+self.returns[(self.returns.index>=startdate) & (self.returns.index<=enddate)]).cumprod()-1
        ax = cumul_rets.plot()
        plt.xlabel('Date')
        plt.ylabel('Return (%)')
        plt.title('Cumulative Returns of ' + self.name +" Portfolio")  
        #format y-axis as percentage
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])          
        plt.tight_layout()
        plt.show()            

def compare_portfolios(portfolios,startdate,enddate):
    cumul_rets = pd.DataFrame()
    for port in portfolios:
        temp_rets =  (1+port.returns[(port.returns.index>=startdate) & (port.returns.index<=enddate)]).cumprod()-1
        cumul_rets = pd.concat([cumul_rets, temp_rets], axis=1, sort=True)
        exp_ret = ((1+port.returns.mean())**252)-1
        vol = port.returns.std()*np.sqrt(252)
        print(port.name + "  (" + port.descrip + ")")
        print("CAGR: %.3f%% \nVolatility: %.3f%% \nSharpe: %.3f" % (100*exp_ret, 100*vol, exp_ret/vol))
        print("____________________________")
            
    ax = cumul_rets.plot()
    plt.xlabel('Date')
    plt.ylabel('Return (%)')
    plt.title('Portfolio Compairison')  
    #format y-axis as percentage
    vals = ax.get_yticks()
    ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])     
    plt.tight_layout()
    plt.show()                    

def load_data(fname, Prices):
    '''load in historical prices'''
    ticker = fname[0:-4]
    data = pd.read_csv("Data/ETF/" + fname)
    data.set_index('Date', inplace=True)
    data = data[["Adj Close"]]
    data.columns = [ticker]
    data.index = pd.to_datetime(data.index)    
    Prices = pd.concat([Prices, data], axis=1, sort=True)
    return Prices
    
    
def EW_positions(Prices):
    '''determine positions in equal weight portfolio'''
    Prices = Prices.dropna(how='any')
    ew = 1/len(list(Prices))
    #set all postions to ew
    Prices[:] = ew
    
    return Prices
    
    
def Trend_Strategy(Prices):
    '''Determine postions based on trends of assets. If price is above 200 day SMA then long else no position'''
    rolling_window = 200
    positions = pd.DataFrame(columns = Prices.columns)
    
    SMA = Prices.rolling(window=rolling_window).mean()
    
    ##plot SMA
    #ax = Prices.plot()
    #SMA.plot(ax=ax)
    #plt.show()
    
    #determine positions
    for day in SMA.index:
        for asset in SMA.columns:
            if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                positions.loc[day,asset] = 1
            else:
                positions.loc[day,asset] = 0
    
    return positions.shift(1).dropna(how='any')
    
if __name__ == "__main__":
    print("Started...")
    #plotting styles
    plt.style.use('ggplot')
    plt.rcParams["figure.figsize"] = (12,7)    
    
    
    #load prices and calculate returns
    Prices = pd.DataFrame()
    
    for fname in os.listdir("Data/ETF"):
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
    
    ##plot cumulative returns
    #startdate = datetime(2016,1,1)
    #enddate = datetime.now()
    #overlapping_rets = Returns[(Returns.index>=startdate) & (Returns.index<=enddate)]  
    #overlapping_rets.dropna(how='any',inplace=True)
    #Cumul_Returns = (1+overlapping_rets).cumprod()-1
    #ax = Cumul_Returns.plot()
    #plt.xlabel('Date')
    #plt.ylabel('Return (%)')
    #plt.title('Cumulative Returns')   
    ##format y-axis as percentage
    #vals = ax.get_yticks()
    #ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])          
    #plt.tight_layout()
    #plt.show()    
    
    
    ############################################################################
    
    
    #testing trend following strategy
    trend_following_pos  = Trend_Strategy(Prices[['SPY']])
    
    #S&P500
    SP500_pos = EW_positions(Prices[['SPY']])
    
    #equal weight postions
    EW_pos = EW_positions(Prices[['SPY','TIP','VNQ','BND']])
    
    #initialize a portfolio
    TF_Port = portfolio("TF","Trend following test porfolio",trend_following_pos)
    SP500_Port = portfolio("S&P500","Just S&P500",SP500_pos)
    EW_Port = portfolio("EW","Equal weight portfolio",EW_pos)
    
    compare_portfolios([SP500_Port,TF_Port,EW_Port],datetime(2007,5,1),datetime.now())
    
    weights = erc_ver1.get_weights(Returns.dropna(how='any'))
    print("Done!")
    