#imports
import pandas as pd
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
#for optimization
from cvxopt import *

#setup mongoDB connection
client = MongoClient("mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true")
db = client['AlphaFactory']  


class portfolio_one:
    
    def __init__(self,etfs,values):
        '''etfs should be a list of ETFs ie. ["SPY","VAB","EEM"] and values should be a list of same length with dollar values in each ETF'''
        #initizliaze main components
        Dollars = pd.Series(values,index=etfs)
        self.initial_value = Dollars.sum()
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

class portfolio_one_b:
    
    def __init__(self,portflio=None):
        '''portfolio should indicate which of alpha factory portfolios, initial value is dollar value'''
        
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

class portfolio_mvo:
    
    def __init__(self,etfs,weights,returns):
        
        Weights = pd.Series(weights,index=etfs)
        
        #returns series of the portfolio
        self.returns = (returns*Weights).sum(axis=1)

    
def portfolio_value_ts(returns,initial_value,startdate=None,enddate=None):
    '''calculate and return time series of portfolio value start to enddate'''
    
    #if no startdate and endate will default to all data
    if not startdate and not enddate:
        rets = returns
    elif not startdate and enddate:
        rets = returns[(returns.index >= startdate)]
    elif startdate and not enddate:
        rets = returns[(returns.index <= enddate)]
    else:
        #trim data based on dates
        rets = returns[(returns.index >= startdate) & (returns.index <= enddate)]
    
    #assume no return on first day, time series represents EOD value
    rets.iloc[0] = 0
    
    #calculate daily value of portfolio
    cumul_value = (1 + rets).cumprod()*initial_value
    
    return cumul_value
    
def portfolio_stats(returns,startdate=None,enddate=None):
    '''calculate statistics of the portfolio over the given date range'''
    
    #if no startdate and endate will default to all data
    if not startdate and not enddate:
        rets = returns
    elif not startdate and enddate:
        rets = returns[(returns.index >= startdate)]
    elif startdate and not enddate:
        rets = returns[(returns.index <= enddate)]
    else:
        #trim data based on dates
        rets = returns[(returns.index >= startdate) & (returns.index <= enddate)]        

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
    sortino = exp_ret/sortino_helper(rets)
    
    #Compile into series
    stat_names = ['CAGR','Volatility','Sharpe','Total Return','Max Drawdown','Sortino']
    Stats = pd.Series([exp_ret,vol,sharpe,cumul_ret,max_dd,sortino],stat_names)
    
    return Stats

def sortino_helper(rets):
    neg_rets = rets[rets < 0]**2
    denom = np.sqrt(neg_rets.sum()/len(rets))*np.sqrt(252)
    return denom   
    
def fetch_data(Prices,ETF):
    print(ETF)
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

def compare_portfolios(startdate,enddate,etfs,values):
    ''''''
    #define dominating portfolio
    dom_port = None
    
    #initialize user inputed portfolio
    user_port = portfolio_one(etfs,values)
    
    #calculate time series for user portfolio
    user_port_ts = portfolio_value_ts(user_port.returns,user_port.initial_value,startdate,enddate)
    
    #calculate stats for user portfolio
    user_port_stats = portfolio_stats(user_port.returns,startdate,enddate)
    
    #initialize all of our portfolios
    our_port_ids = ['Port1']
    our_ports = {}
    our_ports_stats = {}
    for pid in our_port_ids:
        our_ports[pid] = portfolio_one_b()
        #calculate stats for all portfolios
        our_ports_stats[pid] = portfolio_stats(our_ports[pid].returns,startdate,enddate)
        if our_ports_stats[pid]['Sharpe'] >= user_port_stats['Sharpe']:
            dom_port = our_ports[pid]
            dom_port_stats = our_ports_stats[pid]
            dom_port_ts = portfolio_value_ts(dom_port.returns,user_port.initial_value,startdate,enddate)
            print("Selected our portfolio!")
            #no point
            break
    
    #overide (for testing)
    #dom_port = None
    
    if not dom_port:
        #do MVO to determine better allocation
        print("Selected MVO portfolio!")
        
        #convert return back to average
        return_target = ((user_port_stats['CAGR']+1)**(1/252))-1
        
        #load all price data 
                
        Prices = pd.DataFrame()
        
        #assets to include
        etfs = ['ACWV','AGG','DBC','EMB','EMGF','GLD','HYG','IMTM','IQLT','IVLU','MTUM','QUAL','SCHH','SIZE','SPTL','TIP','USMV','VLUE','SHV','SPY']
        
        #get price data for relevant ETFs from mongoDB
        for etf in etfs:
            Prices = fetch_data(Prices,etf)        
        
        #clean and calculate returns
        Prices.dropna(inplace=True,how='any')
        returns = Prices.pct_change()            
        
        #if no startdate and endate will default to all data
        if not startdate and not enddate:
            rets = returns
        elif not startdate and enddate:
            rets = returns[(returns.index >= startdate)]
        elif startdate and not enddate:
            rets = returns[(returns.index <= enddate)]
        else:
            #trim data based on dates
            rets = returns[(returns.index >= startdate) & (returns.index <= enddate)]              
        
        #run mvo optmization
        MVO_wgts = MVO(return_target, rets.iloc[1::])
        
        #calculate characteristics of mvo portfolio
        dom_port = portfolio_mvo(etfs,MVO_wgts,rets)
        dom_port_stats = portfolio_stats(dom_port.returns,startdate,enddate)
        dom_port_ts = portfolio_value_ts(dom_port.returns,user_port.initial_value,startdate,enddate)        
        
    return user_port, user_port_ts, user_port_stats, dom_port, dom_port_ts, dom_port_stats


def MVO(return_target, Returns):
    '''runs mean variance optimization with a inputed target return'''
    
    n=len(list(Returns))
    
    r_avg = np.array(Returns.mean())
    sigma = np.array(Returns.cov())
    
    r_avg = matrix(r_avg)
    sigma = matrix(sigma)    
    
    #define matrices for optimization
    P = sigma
    q = matrix(np.zeros((n, 1)))
    G = matrix(np.concatenate((-np.transpose(np.array(r_avg)), -np.identity(n)), 0))    
    h = matrix(np.concatenate((-np.ones((1,1))*return_target, np.zeros((n,1))), 0))    
    A = matrix(1.0, (1,n))
    b = matrix(1.0)  
    
    #run optimization
    sol = solvers.qp(P, q, G, h, A, b)
    
    #return weights
    return sol['x']


if __name__ == "__main__":
    
    #Note: for actual use, add following line to file 
    #import function1
    
    ##test cases to demonstrate example implentation
    
    ##test 1(Their Portfolio):
    ##initialize portfolio
    #test_portfolio = portfolio_one(['SPY','AGG','SCHH','DBC'],[100,100,100,100])
    
    ##get time series of portfolio value
    #ts_value_1 = portfolio_value_ts(test_portfolio.returns,test_portfolio.initial_value,None,None)
    
    ##plot data
    #ts_value_1.plot()
    #plt.show()
    
    ##get time series for specific date range
    #ts_value_2 = portfolio_value_ts(test_portfolio.returns,test_portfolio.initial_value,datetime(2011,1,1),datetime(2013,1,1))
    
    ##plot data
    #ts_value_2.plot()
    #plt.show()
    
    ##get portfolio stats using all data
    #port_stats_1 = portfolio_stats(test_portfolio.returns,None,None)
    
    ##get portfolio stats for a specific date range
    #port_stats_2 = portfolio_stats(test_portfolio.returns,datetime(2011,1,1),datetime(2013,1,1))
    
    
    ##test 2 (Our Portfolio):
    ##initialize portfolio
    #test_portfolio = portfolio_one_b()
    
    ##get time series of portfolio value
    #ts_value_1 = portfolio_value_ts(test_portfolio.returns,100,None,None)
    
    ##plot data
    #ts_value_1.plot()
    #plt.show()
    
    ##get time series for specific date range
    #ts_value_2 = portfolio_value_ts(test_portfolio.returns,100,datetime(2011,1,1),datetime(2013,1,1))
    
    ##plot data
    #ts_value_2.plot()
    #plt.show()
    
    ##get portfolio stats using all data
    #port_stats_1 = portfolio_stats(test_portfolio.returns,None,None)
    
    ##get portfolio stats for a specific date range
    #port_stats_2 = portfolio_stats(test_portfolio.returns,datetime(2011,1,1),datetime(2013,1,1))
    
    ###############################################
    #Main test (function 1 and function 2 combined)
    ###############################################
    
    #inputs are starddate, enddate and user portolio parameters
    #oututs tuple of 6 elements (user portfolio object, user portfolio time series, user portfolio stats, dominating portfolio object, dominating portfolio time series, dominating portfolio stats)
    
    #test1 should select our portfolio (based on below inputs)
    #test1 = compare_portfolios(datetime(2010,1,1),datetime(2013,1,1),['SPY','AGG','SCHH','DBC'],[100,100,100,100])
    
    #test2 should select the MVO portfolio (based on below inputs)
    test2 = compare_portfolios(datetime(2015,1,1),datetime(2017,1,1),['SPY','AGG','SCHH','DBC'],[100,100,100,100])