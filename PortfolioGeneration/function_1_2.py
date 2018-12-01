#imports
import pandas as pd
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
import time
import statsmodels.api as sm
#for optimization
from cvxopt import *

#setup mongoDB connection
client = MongoClient("mongodb://Daniel_Kecman:M$FCapstone2018@alphafactory-shard-00-00-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-01-y7wfo.gcp.mongodb.net:27017,alphafactory-shard-00-02-y7wfo.gcp.mongodb.net:27017/AlphaFactory?ssl=true&replicaSet=AlphaFactory-shard-0&authSource=admin&retryWrites=true")
db = client['AlphaFactory']  


class portfolio_one:
    
    def __init__(self,etfs,values,Returns):
        '''etfs should be a list of ETFs ie. ["SPY","VAB","EEM"] and values should be a list of same length with dollar values in each ETF'''
        #initizliaze main components
        Dollars = pd.Series(values,index=etfs)
        self.initial_value = Dollars.sum()
        Weights = Dollars/Dollars.sum()
    
        #set market factor
        self.Mkt = Returns['SPY']
                
        #load risk free rate
        self.Rf = load_risk_free()        
        
        #return series of the portfolio
        self.returns = (Returns[etfs]*Weights).sum(axis=1) 

class portfolio_one_b:
    
    def __init__(self,portfolio):
        '''portfolio should indicate which of alpha factory portfolios, initial value is dollar value'''
        
        #get return series from mongoDB
        rets = pd.DataFrame(list(db['Portfolio_Returns'].find({},{"Date":1,portfolio:1,'_id': 0})))
        
        #set index to date
        rets.set_index('Date',inplace=True)
        
        rets.columns = [portfolio]
        
        #convert the index as date
        rets.index = pd.to_datetime(rets.index)            
        rets.sort_index(inplace=True)
        
        #set market factor
        self.Mkt = load_market_factor()     
        
        #load risk free rate
        self.Rf = load_risk_free()          
        
        #return series of the portfolio
        self.returns = rets[portfolio]         

class portfolio_mvo:
    
    def __init__(self,etfs,weights,returns):
        
        Weights = pd.Series(weights,index=etfs)
        
        #load risk free rate
        self.Rf = load_risk_free()  
        
        #set market factor
        self.Mkt = returns['SPY']
        
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
    
def portfolio_stats(portfolio,startdate=None,enddate=None):
    '''calculate statistics of the portfolio over the given date range'''
    
    #if no startdate and endate will default to all data
    if not startdate and not enddate:
        rets = portfolio.returns
    elif not startdate and enddate:
        rets = portfolio.returns[(portfolio.returns.index >= startdate)]
    elif startdate and not enddate:
        rets = portfolio.returns[(portfolio.returns.index <= enddate)]
    else:
        #trim data based on dates
        rets = portfolio.returns[(portfolio.returns.index >= startdate) & (portfolio.returns.index <= enddate)]        

    #assume no return on first day, time series represents EOD value
    rets = rets.iloc[1::]    
    
    #calculation of excess return of 3-month US T-bill
    excess_rets = (rets - portfolio.Rf['Rate']).dropna()
    
    #calculate cumulative returns (used for calculating some statistics)
    cumul_rets = (1 + rets).cumprod()        
    
    #calculate statistics
    
    
    #1.CAGR or expected annual return
    exp_ret = ((1+rets.mean())**252)-1
    
    #2.annualized volatility
    vol = rets.std()*np.sqrt(252)
    
    #3.sharpe   
    sharpe = (((1+excess_rets.mean())**252)-1)/vol   
     
    #4.cumulative return
    cumul_ret = cumul_rets.values[-1]-1
    
    #5.max drawdown
    dd = (1 - cumul_rets.div(cumul_rets.cummax()))*-1
    max_dd = dd.min()
    
    #6.sortino
    sortino = (((1+excess_rets.mean())**252)-1)/sortino_helper(rets) 
    
    #7.VaR
    VaR = Hist_VaR(1, 0.99,rets)
    
    #8.CVaR
    CVaR = Hist_CVaR(1,VaR,rets)    
    
    #9. Beta, Alpha, R-Squared
    beta, alpha, R2 = beta_calc(rets, portfolio.Mkt)
    
    #annualize alpha
    alpha = ((1+alpha)**252)-1
    
    #10. Treynor
    treynor= (((1+excess_rets.mean())**252)-1)/beta    
    
    #Compile into series
    stat_names = ['CAGR','Volatility','Sharpe','Total Return','Max Drawdown','Sortino','VaR','CVaR','Beta','Alpha','R-Squared','Treynor']
    Stats = pd.Series([exp_ret,vol,sharpe,cumul_ret,max_dd,sortino,VaR,CVaR,beta,alpha,R2,treynor],stat_names)
    
    return Stats

def Hist_VaR(days,percentile,rets):
    return rets.quantile(q=(1-percentile),interpolation='lower')
    
def Hist_CVaR(days,VaR,rets):
    temp_data = rets[rets<VaR]
    return temp_data.mean()

def beta_calc(rets, Mkt):
    
    temp_df = pd.concat([rets,Mkt], axis=1,sort=True)
    temp_df.dropna(how='any',inplace=True)
    
    #run regression
    
    # split dependent and independent variable
    X = temp_df['SPY']
    y = temp_df.ix[:,0]
    
    # Add a constant to the independent value
    X1 = sm.add_constant(X)
    
    # make regression model 
    model = sm.OLS(y, X1)
    
    # fit model and print results
    results = model.fit()   
    
    return results.params['SPY'],results.params['const'],results.rsquared


def sortino_helper(rets):
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


def fetch_all_data():
    temp_df = pd.DataFrame(list(db['Raw_Prices'].find({},{'_id': 0})))
    temp_df.set_index('Date',inplace=True)
    #convert the index as date
    temp_df.index = pd.to_datetime(temp_df.index)     
    temp_df.replace("",np.nan,inplace = True)
    temp_df.sort_index(inplace=True)
    return temp_df

def load_risk_free():
    temp_df = pd.DataFrame(list(db['RF'].find({},{'_id': 0})))
    temp_df.set_index('Date',inplace=True)
    #convert the index as date
    temp_df.index = pd.to_datetime(temp_df.index)
    temp_df.sort_index(inplace=True)
    return temp_df

def load_market_factor():
    temp_df = pd.DataFrame(list(db['Raw_Prices'].find({},{'Date':1,'SPY': 1,'_id': 0})))
    temp_df.set_index('Date',inplace=True)
    #convert the index as date
    temp_df.index = pd.to_datetime(temp_df.index)
    temp_df.sort_index(inplace=True)
    return temp_df['SPY'].replace("",np.nan).pct_change()
    
def compare_portfolios(startdate,enddate,etfs,values):
    ''''''
    
    #load all price data 
        
    Prices = pd.DataFrame()
    
    #assets to include
    etf_uni = ['ACWV','AGG','DBC','EMB','EMGF','GLD','HYG','IMTM','IQLT','IVLU','MTUM','QUAL','SCHH','SIZE','SPTL','TIP','USMV','VLUE','SHV','SPY']
    
    #get price data for relevant ETFs from mongoDB
    #for etf in etf_uni:
    #    Prices = fetch_data(Prices,etf)        
    
    #get price data for all ETFs from mongoDB
    Prices = fetch_all_data()
    
    #clean and calculate returns
    Prices.dropna(inplace=True,how='any')
    returns = Prices[etf_uni].pct_change()   
    
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
    
    #define dominating portfolio
    dom_port = None
    
    #initialize user inputed portfolio
    user_port = portfolio_one(etfs,values,rets)
    
    #calculate time series for user portfolio
    user_port_ts = portfolio_value_ts(user_port.returns,user_port.initial_value,None, None)
    
    #calculate stats for user portfolio
    user_port_stats = portfolio_stats(user_port,None, None)
    
    #convert return back to average
    return_target = ((user_port_stats['CAGR']+1)**(1/252))-1        
    
    #initialize all of our portfolios
    port_type = 'Balanced'
    our_port = portfolio_one_b(port_type)
    #calculate stats for all portfolios
    our_port_stats = portfolio_stats(our_port,startdate,enddate)
    if our_port_stats['Sharpe'] >= user_port_stats['Sharpe']:
        dom_port = our_port
        dom_port_stats = our_port_stats
        dom_port_ts = portfolio_value_ts(dom_port.returns,user_port.initial_value,startdate,enddate)
        print("Selected our portfolio!")
        #no point
    
    #overide (for testing)
    #dom_port = None
    
    if not dom_port:
        #do MVO to determine better allocation
        print("Selected MVO portfolio!")        
        
        #run mvo optmization
        MVO_wgts = MVO(return_target, rets.iloc[1::])
        
        #calculate characteristics of mvo portfolio
        dom_port = portfolio_mvo(etf_uni,MVO_wgts,rets)
        dom_port_stats = portfolio_stats(dom_port,None,None)
        dom_port_ts = portfolio_value_ts(dom_port.returns,user_port.initial_value,None,None)        
        
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
    
    print('Running...')
    start = time.time()
    #Note: for actual use, add following line to file 
    #import function1
    
    #test cases to demonstrate example implentation
    
    #test 1(Their Portfolio):
    #initialize portfolio
    
    ###get price data for all ETFs from mongoDB
    Prices = fetch_all_data()
    
    ###clean and calculate returns
    etf_uni = ['ACWV','AGG','DBC','EMB','EMGF','GLD','HYG','IMTM','IQLT','IVLU','MTUM','QUAL','SCHH','SIZE','SPTL','TIP','USMV','VLUE','SHV','SPY']
    Prices.dropna(inplace=True,how='any')
    returns = Prices[etf_uni].pct_change()   
    
    end = time.time()
    print(end - start)        
    
    test_portfolio = portfolio_one(['SPY','AGG','SCHH','DBC'],[100,100,100,100],returns)
    
    ####get time series of portfolio value
    #ts_value_1 = portfolio_value_ts(test_portfolio.returns,test_portfolio.initial_value,None,None)
    
    ####plot data
    #ts_value_1.plot()
    #plt.show()
    
    ##get time series for specific date range
    #ts_value_2 = portfolio_value_ts(test_portfolio.returns,test_portfolio.initial_value,datetime(2008,1,1),datetime(2010,1,1))
    
    ##plot data
    #ts_value_2.plot()
    #plt.show()
    
    ####get portfolio stats using all data
    #port_stats_1 = portfolio_stats(test_portfolio,None,None)
    
    ##get portfolio stats for a specific date range
    #port_stats_2 = portfolio_stats(test_portfolio,datetime(2011,1,1),datetime(2013,1,1))
    
    ##test 2 (Our Portfolio):
    ###initialize portfolio
    #test_portfolio = portfolio_one_b('Balanced')
    
    ###get time series of portfolio value
    #ts_value_1 = portfolio_value_ts(test_portfolio.returns,100,None,None)
    
    ###plot data
    #ts_value_1.plot()
    #plt.show()
    
    ###get time series for specific date range
    #ts_value_2 = portfolio_value_ts(test_portfolio.returns,100,datetime(2008,1,1),datetime(2010,1,1))
    
    ###plot data
    #ts_value_2.plot()
    #plt.show()
    
    ##get portfolio stats using all data
    #port_stats_1 = portfolio_stats(test_portfolio,None,None)
    
    ##get portfolio stats for a specific date range
    #port_stats_2 = portfolio_stats(test_portfolio,datetime(2011,1,1),datetime(2013,1,1))
    
    ###############################################
    #Main test (function 1 and function 2 combined)
    ###############################################
    
    #inputs are starddate, enddate and user portolio parameters
    #oututs tuple of 6 elements (user portfolio object, user portfolio time series, user portfolio stats, dominating portfolio object, dominating portfolio time series, dominating portfolio stats)
    
    start = time.time()
    
    #test1 should select our portfolio (based on below inputs)
    #test1 = compare_portfolios(datetime(2010,1,1),datetime(2013,1,1),['SPY','AGG','SCHH','DBC'],[100,100,100,100])
    
    #test2 should select the MVO portfolio (based on below inputs)
    test2 = compare_portfolios(datetime(2013,1,1),datetime(2016,1,1),['SPY','AGG','SCHH','DBC'],[100,100,100,100])
    
    end = time.time()
    print(end - start)         