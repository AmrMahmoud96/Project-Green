import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
import riskparity as erc_ver1
import riskparity2 as erc_ver2
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas.tseries.offsets import MonthEnd
from datetime import timedelta


class portfolio:
    
    def __init__(self, name, code, descrip, positions,trend,rebal_freq,stat_dyn):
        self.assets = list(positions)
        self.name = name
        self.code = code
        self.descrip = descrip
        self.positions = positions
        self.trend = trend
        self.rebal = rebal_freq
        self.wgt_method = stat_dyn
        self.firstday = positions.index[0]
        self.lastday = positions.index[-1]
        self.calculate_rets()
        self.portfolio_metrics()
        
        
    def portfolio_metrics(self):
        self.exp_ret = ((1+self.returns.mean())**252)-1
        self.vol = self.returns.std()*np.sqrt(252)
        self.sharpe = self.exp_ret/self.vol
        self.sortino = self.sortino_calc()
        cum_returns = (1 + self.returns).cumprod()
        self.dd = (1 - cum_returns.div(cum_returns.cummax()))*-1
        self.maxdd = self.dd.min()
        self.tot_ret = cum_returns.values[-1]-1
        self.VaR = self.Hist_VaR(1, 0.99)
        self.CVaR = self.Hist_CVaR(1)
    
    def sortino_calc(self):
        neg_rets = self.returns[self.returns < 0]**2
        denom = np.sqrt(neg_rets.sum()/len(self.returns))*np.sqrt(252)
        return self.exp_ret/denom
            
    def Hist_VaR(self,days,percentile):
        return self.returns.quantile(q=(1-percentile),interpolation='lower')
    
    def Hist_CVaR(self,days):
        temp_data = self.returns[self.returns<self.VaR]
        return temp_data.mean()
        
    def calculate_rets(self):
        '''calculate portfolio returns based on positions'''
        rets = self.positions*Returns[self.assets]
        rets = rets.dropna()
        self.asset_returns_wgt = rets
        self.returns = rets.sum(axis=1)
        self.returns.name = self.code
        
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
        
    def yearly_returns(self,returns):
        rets = returns + 1
        rets = rets.resample('A').prod()-1
        return rets
    
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
        
        ax1 = plt.subplot2grid((11, 3), (0, 0), colspan=3,rowspan=3)
        ax1.plot(cum_returns)
        
        ax1.set_ylabel('Return (%)',fontsize=9)
        ax1.set_title("Portfolio Tearsheet: " + self.name,y=1.1)  
        ax1.margins(x=0,y=0)
        y_range_add = (cum_returns.max()-cum_returns.min())/20
        ax1.set_ylim(cum_returns.min()-y_range_add,cum_returns.max()+y_range_add)
        ax1.grid(linestyle='--',alpha=0.5,linewidth=0.7)
        ax1.set_axisbelow(True)
        #format y-axis as percentage
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y))) 
        
        ax1.set_facecolor('#FFFFFF')
        
        
        #Chart 2: Drawdown Graph
        ax2 = plt.subplot2grid((11, 3), (3, 0), colspan=3,rowspan=2)
        ax2.plot(self.dd, color = 'red')
        ax2.margins(x=0,y=0)
        ax2.grid(linestyle='--',alpha=0.5,linewidth=0.7)
        #format y-axis as percentage
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))  
        ax2.set_ylim(self.dd.min()*1.05,0)
        ax2.set_ylabel('Drawdown (%)',fontsize=9)
        ax2.set_facecolor('#FFFFFF')          
        ax2.set_axisbelow(True)
        ax2.fill_between(self.dd.index,self.dd.values, alpha=0.5,color='red')
        
        #Table 1: Basic Statitics
        ax4 = plt.subplot2grid((11, 3), (7, 1), rowspan=2, colspan=1)
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
        ax4.text(9.5, 1, '{:.2f}'.format(self.sortino), horizontalalignment='right', fontsize=9)        
        
        ax4.set_title('Statistics',fontsize=10)
        ax4.grid(False)
        ax4.spines['top'].set_linewidth(0.75)
        ax4.spines['bottom'].set_linewidth(0.75)
        ax4.spines['right'].set_visible(False)
        ax4.spines['left'].set_visible(False)
        ax4.get_yaxis().set_visible(False)
        ax4.get_xaxis().set_visible(False)
        ax4.set_ylabel('')
        ax4.set_xlabel('')
        ax4.axis([0, 10, 0, 10])        
        
        #Table 2: Basic Info
        ax6= plt.subplot2grid((11, 3), (7, 0), rowspan=2, colspan=1)
        ax6.text(0.5, 8.5, 'Portfolio Code:', fontsize=9)
        ax6.text(9.5 , 8.5, self.code, horizontalalignment='right', fontsize=9)   
        ax6.text(0.5, 7.0, 'Start Date:', fontsize=9)
        ax6.text(9.5 , 7.0, self.firstday.date(), horizontalalignment='right', fontsize=9)
        ax6.text(0.5, 5.5, 'End Date:', fontsize=9)
        ax6.text(9.5 , 5.5, self.lastday.date(), horizontalalignment='right', fontsize=9)   
        ax6.text(0.5, 4.0, 'Rebalanced:', fontsize=9)
        ax6.text(9.5 , 4.0, self.rebal, horizontalalignment='right', fontsize=9)
        ax6.text(0.5, 2.5, 'Trend Following:', fontsize=9)
        ax6.text(9.5 , 2.5, self.trend, horizontalalignment='right', fontsize=9)    
        ax6.text(0.5, 1, 'Weighting:', fontsize=9)
        ax6.text(9.5, 1, self.wgt_method, horizontalalignment='right', fontsize=9)              
        
        ax6.set_title('Overview',fontsize=10)
        ax6.grid(False)
        ax6.spines['top'].set_linewidth(0.75)
        ax6.spines['bottom'].set_linewidth(0.75)
        ax6.spines['right'].set_visible(False)
        ax6.spines['left'].set_visible(False)
        ax6.get_yaxis().set_visible(False)
        ax6.get_xaxis().set_visible(False)
        ax6.set_ylabel('')
        ax6.set_xlabel('')
        ax6.axis([0, 10, 0, 10])    
        
        #Table 3: Basic Info
        ax6= plt.subplot2grid((11, 3), (7, 2), rowspan=2, colspan=1)
        ax6.text(0.5, 8.5, r'$VaR_{99\%}:$', fontsize=9)
        ax6.text(9.5 , 8.5, '{:.2%}'.format(self.VaR), horizontalalignment='right', fontsize=9)   
        ax6.text(0.5, 7.0, r'$CVaR_{99\%}:$', fontsize=9)
        ax6.text(9.5 , 7.0, '{:.2%}'.format(self.CVaR), horizontalalignment='right', fontsize=9)
        ax6.text(0.5, 5.5, 'Placeholder:', fontsize=9)
        ax6.text(9.5 , 5.5, 'N/A', horizontalalignment='right', fontsize=9)   
        ax6.text(0.5, 4.0, 'Placeholder:', fontsize=9)
        ax6.text(9.5 , 4.0, 'N/A', horizontalalignment='right', fontsize=9)
        ax6.text(0.5, 2.5, 'Placeholder:', fontsize=9)
        ax6.text(9.5 , 2.5, 'N/A', horizontalalignment='right', fontsize=9)    
        ax6.text(0.5, 1, 'Placeholder', fontsize=9)
        ax6.text(9.5, 1, 'N/A', horizontalalignment='right', fontsize=9)        
        
        ax6.set_title('Statistics #2',fontsize=10)
        ax6.grid(False)
        ax6.spines['top'].set_linewidth(0.75)
        ax6.spines['bottom'].set_linewidth(0.75)
        ax6.spines['right'].set_visible(False)
        ax6.spines['left'].set_visible(False)
        ax6.get_yaxis().set_visible(False)
        ax6.get_xaxis().set_visible(False)
        ax6.set_ylabel('')
        ax6.set_xlabel('')
        ax6.axis([0, 10, 0, 10])    
                
        
        #Table 3
        ax7 = plt.subplot2grid((11, 3), (9, 2), rowspan=2, colspan=1)
        yearly_rets = self.yearly_returns(self.returns)
        ax7.bar(yearly_rets.index.strftime("%Y"),yearly_rets.values,width=0.8,alpha=1)
        #format y-axis as percentage
        ax7.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y))) 
        ax7.set_xticklabels(yearly_rets.index.strftime("%Y"),rotation = '70',horizontalalignment='center',fontsize=8)
        #ax7.xaxis_date()
        ax7.set_facecolor('#FFFFFF')
        ax7.set_axisbelow(True)
        ax7.grid(linestyle='--',alpha=0.5,linewidth=0.7)
        ax7.set_title('Yearly Returns (%)',fontsize=10)
        #ax7.plot(yearly_rets,type='bar')
        
        #Positioning Chart
        ax5 = plt.subplot2grid((11, 3), (5, 0), rowspan=2, colspan=3)
        ax5.stackplot(self.positions.index,self.positions.T,labels = self.positions.columns,alpha=1)
        ax5.grid(linestyle='--',alpha=0.5,linewidth=0.7,axis='y')
        ax5.set_axisbelow(True)
        ax5.margins(x=0,y=0)
        ax5.set_ylim(0,1)
        #ax5.legend(loc=8,ncol=len(list(self.positions)),mode=None,bbox_to_anchor=(0., 1.02, 1., .102),fontsize=8,edgecolor="#FFFFFF")
        ax5.legend(loc=8,ncol=len(list(self.positions)),mode=None,bbox_to_anchor=(0., 1.02, 1., .102),fontsize=7,edgecolor="#FFFFFF",handlelength=0.6)
        ax5.set_ylabel('Weight (%)',fontsize=9)
        
        #format y-axis as percentage
        ax5.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))        
        ax5.set_facecolor('#FFFFFF')          
        
        #Heatmap
        ax10 = plt.subplot2grid((11, 3), (9, 0), rowspan=2, colspan=2)
        assets_rets = self.yearly_returns(self.asset_returns_wgt)
        sns.heatmap(assets_rets.T, linewidth=0.5, yticklabels=True,ax=ax10,xticklabels=assets_rets.index.strftime("%Y"), center=0, annot=True, cbar=False, fmt='.1%', cmap='RdYlGn',annot_kws={"size": 6.5})
        #ax10.set_yticklabels(ax10.get_yticklabels(),rotation=0,fontsize=8)
        ax10.set_yticklabels(ax10.get_yticklabels(),rotation=0,fontsize=6)
        ax10.set_xticklabels(ax10.get_xticklabels(),fontsize=8,rotation = 70)
        ax10.tick_params(axis='both',bottom=False,left=False)
        ax10.set_xlabel('')
        ax10.set_title('Performance Attribution',fontsize=10)
        #generate plot    
        plt.tight_layout()

        #plt.show()
        
        #save tearsheet
        plt.subplots_adjust(left=0.115, right=0.95, top=0.93,bottom=0.07)
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
 
def EW_TF_positions(Prices,rebal_freq,rolling_window):
    '''determine postions in equal weight portfolio with trend following overlay'''
    Prices = Prices.dropna(how='any')
    positions = pd.DataFrame(columns = Prices.columns)
    assets = list(Prices)
    ew = 1/len(assets)    
    SMA = Prices.rolling(window=rolling_window).mean()
    SMA = SMA.iloc[200:]
    #determine positions
    if rebal_freq == 'D':
        for day in SMA.index:
            for asset in SMA.columns:
                if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                    positions.loc[day,asset] = 1
                else:
                    positions.loc[day,asset] = 0
        
        return positions.shift(1).dropna(how='any')*ew 
    else:
        day = SMA.index[0]
        new_day = day
        while day <= SMA.index[-1]:
            if day in SMA.index:
                if day >= new_day:
                    for asset in SMA.columns:
                        if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                            positions.loc[day,asset] = 1
                        else:
                            positions.loc[day,asset] = 0
                    positions.loc[day] = positions.loc[day]*ew
                    last_pos = positions.loc[day]
                    if rebal_freq == 'M':
                        new_day = day + pd.DateOffset(months=1)
                    if rebal_freq == 'Y':
                        new_day = day + pd.DateOffset(years=1)
                    day = day + timedelta(days=1)
                else:
                    temp_data = last_pos*(1+Returns[assets].loc[day])
                    #if temp_data.sum() > 1:
                        #positions.loc[day] = temp_data/temp_data.sum()
                    #else:
                        #positions.loc[day] = temp_data
                    if temp_data.astype(bool).sum() == len(assets):
                        positions.loc[day] = temp_data/temp_data.sum()
                    else:
                        positions.loc[day] = temp_data                        
                    #positions = positions.loc[:,:].div(positions.sum(axis=1),axis=0)
                    last_pos = positions.loc[day]                    
                    day = day + timedelta(days=1)
            else:
                day = day + timedelta(days=1)            
        return positions.shift(1).dropna(how='any')        
    
def EW_positions(Prices,rebal_freq='D'):
    '''determine positions in equal weight portfolio'''
    Prices = Prices.dropna(how='any')
    assets = list(Prices)
    ew = 1/len(assets)
    if rebal_freq == 'D':
        #set all postions to ew
        Prices[:] = ew
        positions = Prices
    else:
        positions = pd.DataFrame(columns = Prices.columns)
        day = Prices.index[0]
        new_day = day
        while day <= Prices.index[-1]:
            if day in Prices.index:
                if day >= new_day:
                    positions.loc[day] = ew
                    last_pos = ew
                    if rebal_freq == 'M':
                        new_day = day + pd.DateOffset(months=1)
                    if rebal_freq == 'Y':
                        new_day = day + pd.DateOffset(years=1)
                    if rebal_freq == 'W':
                        new_day = day + pd.DateOffset(weeks=1)                    
                    day = day + timedelta(days=1)
                else:
                    positions.loc[day] = last_pos*(1+Returns[assets].loc[day])
                    last_pos = positions.loc[day]                    
                    day = day + timedelta(days=1)
                    
            else:
                day = day + timedelta(days=1)            
    return realloc(positions.shift(1).dropna(how='any'))

def risk_parity_positions(Prices):
    Prices = Prices.dropna(how='any')
    weights = erc_ver1.get_weights(Prices.pct_change().dropna(how='any'))
    positions = Prices.copy()
    for asset in positions.columns:
        positions[asset] = weights[asset]
    return positions

def risk_parity_generator_V2(Prices,rebal_freq,TF=None, rolling_window=None,static=False,target=None,cash='SHV'):
    '''generate positions for risk parity portfolio'''
    Prices = Prices.dropna(how='any')
    assets = list(Prices)
    assets_cash = assets.copy()
    assets_cash.remove(cash)
    positions = pd.DataFrame(columns = assets)
    static_weights = erc_ver1.get_weights(Prices[assets_cash].pct_change().dropna(how='any'),target)
    
    #if trend following option selected
    if TF:
        SMA = Prices.rolling(window=rolling_window).mean()
        SMA = SMA.iloc[rolling_window:]
        day = SMA.index[0]
        new_day = day
        while day <= SMA.index[-1]:
            if day in SMA.index:
                if day >= new_day:
                    if static:
                        weights = static_weights
                    else:
                        weights = erc_ver1.get_weights(Prices[assets_cash].loc[Prices.index <= day].iloc[-1*rolling_window::].pct_change().dropna(how='any'),target)
                    for asset in SMA.columns:
                        if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                            positions.loc[day,asset] = 1
                        else:
                            positions.loc[day,asset] = 0
                    positions.loc[day,cash]=0
                    last_pos = positions.loc[day]*weights
                    last_pos.loc[cash] = 1 - last_pos.sum()
                    positions.loc[day] = last_pos
                    
                    if rebal_freq == 'M':
                        new_day = day + pd.DateOffset(months=1)
                    if rebal_freq == 'Y':
                        new_day = day + pd.DateOffset(years=1)
                    day = day + timedelta(days=1)
                else:
                    temp_data = last_pos*(1+Returns[assets].loc[day])
                    positions.loc[day] = temp_data/temp_data.sum()
                    #if temp_data.astype(bool).sum() == len(assets):
                    #    positions.loc[day] = temp_data/temp_data.sum()
                    #else:
                    #    positions.loc[day] = temp_data  
                    last_pos = positions.loc[day]                    
                    day = day + timedelta(days=1)                    
            else:
                day = day + timedelta(days=1)
                
        return positions.shift(1).dropna(how='any')
    else:
        day = Prices.index[rolling_window]
        new_day = day
        while day <= Prices.index[-1]:
            if day in Prices.index:
                if day >= new_day:
                    if static:
                        weights = static_weights
                    else:
                        weights = erc_ver1.get_weights(Prices.loc[Prices.index <= day].iloc[-1*rolling_window::].pct_change().dropna(how='any'),target)
                    positions.loc[day] = weights
                    last_pos = weights
                    if rebal_freq == 'M':
                        new_day = day + pd.DateOffset(months=1)
                    if rebal_freq == 'Y':
                        new_day = day + pd.DateOffset(years=1)
                    day = day + timedelta(days=1)
                else:
                    temp_data = last_pos*(1+Returns[assets].loc[day])
                    if temp_data.astype(bool).sum() == len(assets):
                        positions.loc[day] = temp_data/temp_data.sum()
                    else:
                        positions.loc[day] = temp_data  
                    last_pos = positions.loc[day]                    
                    day = day + timedelta(days=1)                    
            else:
                day = day + timedelta(days=1)
                
        return positions.shift(1).dropna(how='any')        

def risk_parity_generator(Prices,freq,TF=None, rolling_window=None):
    '''generate positions for risk parity portfolio'''
    Prices = Prices.dropna(how='any')
    #get ERC weights
    weights = erc_ver1.get_weights(Prices.pct_change().dropna(how='any'))
    
    #if trend following option selected
    if TF:
        positions = pd.DataFrame(columns = Prices.columns)
        SMA = Prices.rolling(window=rolling_window).mean()
        SMA = SMA.iloc[200:]
        
        day = SMA.index[0]
        new_day = day
        while day <= SMA.index[-1]:
            if day in SMA.index:
                if day >= new_day:
                    for asset in SMA.columns:
                        if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                            positions.loc[day,asset] = 1
                        else:
                            positions.loc[day,asset] = 0
                    last_pos = positions.loc[day]
                    new_day = day + pd.DateOffset(months=1)
                    day = day + timedelta(days=1)
                else:
                    day = day + timedelta(days=1)
                    positions.loc[day] = last_pos
            else:
                day = day + timedelta(days=1)
        positions = positions.shift(1).dropna(how='any')*weights
    
    else:
        positions = Prices.copy()
        for asset in positions.columns:
            positions[asset] = weights[asset]        
    return positions

def risk_parity_tf_positions(Prices):
    Prices = Prices.dropna(how='any')
    weights = erc_ver1.get_weights(Prices.pct_change().dropna(how='any'))
    rolling_window = 200
    positions = pd.DataFrame(columns = Prices.columns)
    SMA = Prices.rolling(window=rolling_window).mean()
    SMA = SMA.iloc[200:]    
    for day in SMA.index:
        for asset in SMA.columns:
            if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                positions.loc[day,asset] = 1
            else:
                positions.loc[day,asset] = 0
    return positions.shift(1).dropna(how='any')*weights

def risk_parity_tf_positions_realloc(Prices):
    Prices = Prices.dropna(how='any')
    weights = erc_ver1.get_weights(Prices.pct_change().dropna(how='any'))
    rolling_window = 200
    positions = pd.DataFrame(columns = Prices.columns)
    SMA = Prices.rolling(window=rolling_window).mean()
    SMA = SMA.iloc[200:]    
    for day in SMA.index:
        for asset in SMA.columns:
            if Prices.loc[day,asset] >= SMA.loc[day,asset]:
                positions.loc[day,asset] = 1
            else:
                positions.loc[day,asset] = 0
    positions = positions.shift(1).dropna(how='any')*weights
    positions = realloc(positions)
    return positions

def realloc(positions):
    positions = positions.loc[:,:].div(positions.sum(axis=1),axis=0)
    return positions
        
def inverse_vol(returns):
    inv_vol = 1/returns.std()
    weights = inv_vol/inv_vol.sum()
    return weights

if __name__ == "__main__":
    
    print("Started...")
    
    #plotting styles
    plt.rcParams["figure.figsize"] = (12,7)    
    plt.rcParams.update({'font.size': 9})
    plt.rcParams.update({'mathtext.default':  'regular' })
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#aec7e8','#ffbb78','#98df8a','#ff9896','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf'])
    
    #set Leverage
    ###############
    leverage = None
    ###############
    
    #load prices
    Prices = pd.DataFrame()
    for fname in os.listdir("Data/ETF"):
        Prices = load_data(fname,Prices)
    #calculate returns
    Returns = Prices.pct_change() 
    #####Same Date Range#####
    #Prices = Prices[(Prices.index >= datetime(2008,10,6)) & (Prices.index <= datetime(2018,10,11))]
    
    ################LEVERAGE########################
    if leverage:
        Returns = Returns*leverage
    
    print("Prices and returns loaded!")
    
    ############################################################################
    ############################## Plotting Tests ##############################
    ############################################################################
    
    #basic plot test
    #Prices['SHV'].plot()
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
    
    #Determine Positions
        
    #equal weight positions
    #EW_pos = EW_positions(Prices[['SPY','VNQ','BND','EEM','EFA','TIP','GLD']])
    #EW_Port = portfolio("Equal Weight","EW","Equal weight portfolio",EW_pos)
    
    #equal weight positions rebalanced every 30 days
    #EW_pos = EW_positions(Prices[['SPY']],'M')
    #EW_Port = portfolio("S&P500","SP500","Equal weight portfolio",EW_pos,'N/A','N/A','N/A')
    
    #equal weight with trend following overlay
    #EW_TF_pos = EW_TF_positions(Prices,'M',150)
    #EW_TF_Port = portfolio("Trend Following Equal Weight","EW_TF","Equal weight portfolio with trend following overlay",EW_TF_pos,'150 SMA', 'Monthly','EW')
    
    #risk parity weights
    #RP_pos = risk_parity_positions(Prices[['SPY','TIP','VNQ','BND']])
    #RP_Port = portfolio("Static Risk Parity","RP","Risk parity portfolio with static weights",RP_pos)
    
    #risk pairty with trend following overlay
    #RP_TF_pos = risk_parity_tf_positions(Prices[['SPY','TIP','VNQ','BND']])
    #RP_TF_Port = portfolio("Static Risk Parity with TF","RP_TF","Risk parity portfolio with static weights and trend following overlay",RP_TF_pos)
    
    #risk parity with trend following realloc overlay
    #RP_TF_RA_pos = risk_parity_tf_positions_realloc(Prices[['SPY','TIP','VNQ','BND']])
    #RP_TF_RA_Port = portfolio("Static Risk Parity with TF Realloc","RP_TF_RA","Risk parity portfolio with static weigths and trend following overlay that ensures full investment at all times",RP_TF_RA_pos)
    
    #RP_pos = risk_parity_generator(Prices[['SPY','VNQ','BND','EEM','MUB','TIP','GLD']],'M',TF=True, rolling_window=200)
    #RP_TF_Port = portfolio("Static Risk Parity Monthly TF","RP_TF","Risk parity portfolio with static weights and trend following overlay",RP_pos)
    #target = [.15,.15,.15,.05,.15,.05,.05,.05,.05,.05,.05,.05]
    RP_pos = risk_parity_generator_V2(Prices[['SPY','EFA','EEM','DBC','VNQ','GLD','TIP','EMB','BWX','TLT','MUB','AGG','SHV']],'M',TF=True, rolling_window=200,static=False,target=None)
    RP_Port = portfolio("Risk Parity","RP","Risk parity portfolio with dynamic weights reblanced monthly",RP_pos, '200 SMA','Monthly','RP 200')
    
    #RP_TF_pos = risk_parity_generator_V2(Prices,'M',TF=True, rolling_window=200)
    #RP_TF_Port = portfolio("Dynamic Risk Parity Trend Following","RP_TF","Risk parity portfolio with dynamic weights reblanced monthly and Trend Following Overlay",#RP_TF_pos, '200 SMA','Monthly','RP 200')     

    #compare_portfolios([SP500_Port,TF_Port,EW_Port],datetime(2007,5,1),datetime.now())
    
    #weights_1 = erc_ver1.get_weights(Returns.dropna(how='any'))
    #weights_2 = erc_ver2.get_weights(Returns.dropna(how='any'))
    print("Done!")
    