#imports
import pandas as pd
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime

#setup mongoDB connection
client = MongoClient("mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true")
db = client['AlphaFactory']  

class portfolio_one:
    
    def __init__(self,etfs,values):
        '''etfs should be a list of ETFs ie. ["SPY","VAB","EEM"] and values should be a list of same length with dollar values in each ETF'''
        #initizliaze main components
        Dollars = pd.Series(values,index=etfs)
        self.init_value = Dollars.sum()
        Weights = Dollars/Dollars.sum()
        Prices = pd.DataFrame()
       
        #get price data for relevant ETFs from mongoDB
        for etf in etfs:
            Prices = fetch_data(Prices,etf)        
        
        #clean and calculate returns
        Prices.dropna(inplace=True,how='any')
        Returns = Prices.pct_change()
        
        #return series of the portfolio
        self.returns = (Returns*Weights).sum(axis=1)          
    
    def portfolio_value_ts(self,startdate=None,enddate=None):
        '''calculate and return time series of portfolio value start to enddate'''
        
        #if no startdate and endate will default to all data
        if not startdate and not enddate:
            rets = self.returns
        elif not startdate and enddate:
            rets = self.returns[(self.returns.index >= startdate)]
        elif startdate and not enddate:
            rets = self.returns[(self.returns.index <= enddate)]
        else:
            #trim data based on dates
            rets = self.returns[(self.returns.index >= startdate) & (self.returns.index <= enddate)]
        
        #assume no return on first day, time series represents EOD value
        rets.iloc[0] = 0
        
        #calculate daily value of portfolio
        cumul_value = (1 + rets).cumprod()*self.init_value
        
        return cumul_value
    
    def portfolio_stats(self,startdate=None,enddate=None):
        '''calculate statistics of the portfolio over the given date range'''
        
        #if no startdate and endate will default to all data
        if not startdate and not enddate:
            rets = self.returns
        elif not startdate and enddate:
            rets = self.returns[(self.returns.index >= startdate)]
        elif startdate and not enddate:
            rets = self.returns[(self.returns.index <= enddate)]
        else:
            #trim data based on dates
            rets = self.returns[(self.returns.index >= startdate) & (self.returns.index <= enddate)]        
        
        #calculate cumulative returns (used for calculating some statistics)
        cumul_rets = (1 + rets).cumprod()        
        
        #calculate statistics
        
        #1.CAGR or expected annual return
        exp_ret = ((1+rets.mean())**252)-1
        
        #2.annualized volatility
        vol = rets.std()*np.sqrt(252)
        
        #3.sharpe
        sharpe = exp_ret/vol       
        
        #4.cumulative return
        cumul_ret = cumul_rets.values[-1]-1
        
        #5.max drawdown
        dd = (1 - cumul_rets.div(cumul_rets.cummax()))*-1
        max_dd = dd.min()
        
        #6.sortino
        sortino = exp_ret/self.sortino_helper(rets)
        
        #Compile into series
        stat_names = ['CAGR','Volatility','Sharpe','Total Return','Max Drawdown','Sortino']
        Stats = pd.Series([exp_ret,vol,sharpe,cumul_ret,max_dd,sortino],stat_names)
        
        return Stats
    
    def sortino_helper(self,rets):
        neg_rets = rets[rets < 0]**2
        denom = np.sqrt(neg_rets.sum()/len(rets))*np.sqrt(252)
        return denom
    
def fetch_data(Prices,ETF):
    #get data from mongodb
    temp_df = pd.DataFrame(list(db[ETF].find({},{"Date":1,"Adj Close":1,'_id': 0})))
    
    #set index to date
    temp_df.set_index('Date',inplace=True)
    temp_df.columns = [ETF]
    
    #convert the index as date
    temp_df.index = pd.to_datetime(temp_df.index)    
    
    #update main DF
    Prices = pd.concat([Prices, temp_df], axis=1, sort=True)
    return Prices


if __name__ == "__main__":
    
    #Note: for actual use, add following line to file 
    #from function_one import portfolio_one
    
    #test cases to demonstrate example implentation
    
    #temp_df = pd.DataFrame(list(db['SPY'].find({},{"Date":1,"Adj Close":1,'_id': 0})))
    #test 1:
    #initialize portfolio (Equity,Bonds,Real Estate, Commodities)
    test_portfolio = portfolio_one(['SPY','AGG','SCHH','DBC'],[100,100,100,100])
    
    ##get time series of portfolio value
    ts_value_1 = test_portfolio.portfolio_value_ts(None,None)
    
    ##plot data
    ts_value_1.plot()
    plt.show()
    
    ##get time series for specific date range
    ts_value_2 = test_portfolio.portfolio_value_ts(datetime(2011,1,1),datetime(2013,1,1))
    
    ##plot data
    ts_value_2.plot()
    plt.show()
    
    ##get portfolio stats using all data
    port_stats_1 = test_portfolio.portfolio_stats(None,None)
    
    ##get portfolio stats for a specific date range
    port_stats_2 = test_portfolio.portfolio_stats(datetime(2011,1,1),datetime(2013,1,1))
    