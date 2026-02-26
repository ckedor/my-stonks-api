import pandas as pd

from .helpers import calc_periods_per_year


def annualize_rets(r):
    """
    Annualizes a set of returns 
    """
    componded_growth = (1+r).prod()
    n_periods = r.shape[0]
    periods_per_year = calc_periods_per_year(r)
    return float(componded_growth**(periods_per_year/n_periods)-1)

def annualize_vol(r):
    """ 
    Annualizes the vol of a set of returns 
    """
    periods_per_year = calc_periods_per_year(r)
    return r.std(ddof=0)*(periods_per_year**0.5)

def sharpe_ratio_from_annual_rate(r, riskfree_rate):
    """
    Computes the annualized sharpe ratio of a set of returns
    """
    periods_per_year = calc_periods_per_year(r)
    rf_per_period = (1 + riskfree_rate)**(1/periods_per_year)-1
    excess_ret = r - rf_per_period
    ann_ex_ret = annualize_rets(excess_ret)
    ann_vol = annualize_vol(r)
    return ann_ex_ret/ann_vol

def sharpe_ratio(r, riskfree_returns):
    """
    Computes the annualized sharpe ratio of a set of returns given a risk-free return series.
    """
    aligned = pd.concat([r, riskfree_returns], axis=1, join="inner").dropna()
    asset_r = aligned.iloc[:, 0]
    rf_r = aligned.iloc[:, 1]

    excess_ret = asset_r - rf_r
    ann_ex_ret = annualize_rets(excess_ret)
    ann_vol = annualize_vol(asset_r)

    return ann_ex_ret / ann_vol