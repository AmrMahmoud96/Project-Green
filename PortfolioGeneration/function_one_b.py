#imports
import pandas as pd
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime

#setup mongoDB connection
client = MongoClient("mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true")
db = client['AlphaFactory']  

class portfolio_one_b:
    
    def __init__(self,initial_value,portflio=None):
        '''portfolio should indicate which of alpha factory portfolios, initial value is dollar value'''
        
        self.init_value = initial_value
        
        #get retrun series from mongoDB
        #currently only works for one portfolio

        rets = pd.DataFrame(list(db['Portfolio_One_Returns'].find({},{"Date":1,"Return":1,'_id': 0})))
       
        #set index to date
        rets.set_index('Date',inplace=True)
        rets.columns = ['Portfolio1']
        
        #convert the index as date
        rets.index = pd.to_datetime(rets.index)            
        
        #return series of the portfolio
        self.returns = rets['Portfolio1']         
    
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
    
        #assume no return on first day, time series represents EOD value
        rets.iloc[0] = 0        
    
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
    
if __name__ == "__main__":
    
    #Note: for actual use, add following line to file 
    #from function_one import portfolio_one
    
    #test cases to demonstrate example implentation
    
    #test 1:
    #initialize portfolio
    test_portfolio = portfolio_one_b(100)
    
    #get time series of portfolio value
    ts_value_1 = test_portfolio.portfolio_value_ts(None,None)
    
    #plot data
    ts_value_1.plot()
    plt.show()
    
    #get time series for specific date range
    ts_value_2 = test_portfolio.portfolio_value_ts(datetime(2011,1,1),datetime(2013,1,1))
    
    #plot data
    ts_value_2.plot()
    plt.show()
    
    #get portfolio stats using all data
    port_stats_1 = test_portfolio.portfolio_stats(None,None)
    
    #get portfolio stats for a specific date range
    port_stats_2 = test_portfolio.portfolio_stats(datetime(2011,1,1),datetime(2013,1,1))
    