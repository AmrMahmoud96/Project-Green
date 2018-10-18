import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
import riskparity as erc_ver1
import riskparity2 as erc_ver2


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
        cum_returns = (1 + self.returns).cumprod()
        self.dd = (1 - cum_returns.div(cum_returns.cummax()))*-1
        self.maxdd = self.dd.min()
        self.tot_ret = cum_returns.values[-1]-1
        
    
    def calculate_rets(self):
        '''calculate portfolio returns based on positions'''
        rets = self.positions*Returns[self.assets]
        rets = rets.dropna()
        self.returns = rets.sum(axis=1)
        self.returns.name = self.name
        
    def plot_dd(self,startdate,enddate):
        '''plot drawdown plot'''
        if not startdate:
            startdate = self.firstday
        if not enddate:
            enddate = self.lastday        
        ax = self.dd.plot()
        plt.ylabel('Drawdown (%)')
        plt.title('Underwater Chart - ' + self.name +" Portfolio")  
        #format y-axis as percentage
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])          
        plt.tight_layout()
        plt.fill_between(self.dd.index,self.dd.values, alpha=0.8)
        plt.show()          
        
    
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
        plt.title('Cumulative Returns - ' + self.name +" Portfolio")  
        #format y-axis as percentage
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])          
        plt.tight_layout()
        plt.show()                    
   
    def tearsheet(self,startdate,enddate):
        #8.5X11 so that can fit on standard page
        plt.rcParams["figure.figsize"] = (8.5,11)  
        
        #Chart 1: Cumulative Return
        cum_returns = (1 + self.returns).cumprod()-1
        
        ax1 = plt.subplot2grid((10, 3), (0, 0), colspan=3,rowspan=3)
        ax1.plot(cum_returns)
        
        ax1.set_ylabel('Return (%)')
        ax1.set_title("Portfolio Tearsheet: " + self.name,y=1.1)  
        ax1.margins(x=0,y=0)
        ax1.grid(linestyle='-')
        #format y-axis as percentage
        vals = ax1.get_yticks()
        ax1.set_yticklabels(['{:,.0%}'.format(x) for x in vals])                
        ax1.set_facecolor('#F0F0F0')
        
        #Chart 2: Drawdown Graph
        ax2 = plt.subplot2grid((10, 3), (3, 0), colspan=3,rowspan=2)
        ax2.plot(self.dd, color = 'red')
        ax2.margins(x=0,y=0)
        ax2.grid(linestyle='-')
        #format y-axis as percentage
        vals = ax2.get_yticks()
        ax2.set_yticklabels(['{:,.0%}'.format(x) for x in vals])                
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_facecolor('#F0F0F0')          
        ax2.fill_between(self.dd.index,self.dd.values, alpha=0.5,color='red')
        
        #Table 1: Basic Statitics
        ax4 = plt.subplot2grid((10, 3), (5, 0), rowspan=2, colspan=1)
        ax4.text(0.5, 8.5, 'Total Return:', fontsize=9)
        ax4.text(9.5 , 8.5, '{:.2%}'.format(self.tot_ret), horizontalalignment='right', fontsize=9)   
        ax4.text(0.5, 7.0, 'CAGR:', fontsize=9)
        ax4.text(9.5 , 7.0, '{:.2%}'.format(self.exp_ret), horizontalalignment='right', fontsize=9)
        ax4.text(0.5, 5.5, 'Annual Volatility:', fontsize=9)
        ax4.text(9.5 , 5.5, '{:.2%}'.format(self.vol), horizontalalignment='right', fontsize=9)   
        ax4.text(0.5, 4.0, 'Sharpe:', fontsize=9)
        ax4.text(9.5 , 4.0, '{:.2f}'.format(self.sharpe), horizontalalignment='right', fontsize=9)
        ax4.text(0.5, 2.5, 'Max Drawdown:', fontsize=9)
        ax4.text(9.5 , 2.5, '{:.2%}'.format(self.maxdd), horizontalalignment='right', fontsize=9)    
        ax4.text(0.5, 1, 'Sortino:', fontsize=9)
        ax4.text(9.5, 1, 'N/A', horizontalalignment='right', fontsize=9)        
        
        ax4.set_title('Statistics',fontsize=11)
        ax4.grid(False)
        ax4.spines['top'].set_linewidth(1.0)
        ax4.spines['bottom'].set_linewidth(1.0)
        ax4.spines['right'].set_visible(False)
        ax4.spines['left'].set_visible(False)
        ax4.get_yaxis().set_visible(False)
        ax4.get_xaxis().set_visible(False)
        ax4.set_ylabel('')
        ax4.set_xlabel('')
        ax4.axis([0, 10, 0, 10])        
        
        
        ax6= plt.subplot2grid((10, 3), (5, 1), rowspan=2, colspan=1)
        ax7 = plt.subplot2grid((10, 3), (5, 2), rowspan=2, colspan=1)
        
        #Positioning Chart
        ax5 = plt.subplot2grid((10, 3), (7, 0), rowspan=2, colspan=3)
        ax5.stackplot(self.positions.index,self.positions.T,labels = self.positions.columns,alpha=0.9)
        ax5.margins(x=0,y=0)
        ax5.legend(loc='upper left')
        ax5.set_ylabel('Weight (%)')
        #format y-axis as percentage
        vals = ax5.get_yticks()
        ax5.set_yticklabels(['{:,.0%}'.format(x) for x in vals])          
        ax5.set_facecolor('#F0F0F0')          
        
        #generate plot
        plt.tight_layout()

        #plt.show()
        
        #save tearsheet
        plt.subplots_adjust(left=0.13, right=0.92, top=0.915)
        plt.savefig('Tearsheet.png')
        plt.savefig('Tearsheet.pdf')
        
        #reset figsize to standard
        plt.rcParams["figure.figsize"] = (12,7)

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
    #plt.style.use('ggplot')
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
    
    #compare_portfolios([SP500_Port,TF_Port,EW_Port],datetime(2007,5,1),datetime.now())
    
    #weights_1 = erc_ver1.get_weights(Returns.dropna(how='any'))
    #weights_2 = erc_ver2.get_weights(Returns.dropna(how='any'))
    print("Done!")
    