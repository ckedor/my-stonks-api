import pandas as pd


def calculate_portfolio_daily_returns(pos_df):
    df = pos_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['date', 'asset_id'])

    df['value'] = df['quantity'] * df['price']
    df['contribution'] = (
        df.groupby('asset_id')['quantity'].diff().fillna(0) * df['price']
    )
    df['net_value_day'] = df.groupby('date')['value'].transform('sum') - df.groupby('date')['contribution'].transform('sum')

    df['asset_return'] = df.groupby('asset_id')['price'].pct_change()
    base_valor = df['value'] - df['contribution']
    df['asset_return'] += df['dividend'] / base_valor.replace(0, pd.NA)
    df['asset_return'] = df['asset_return'].fillna(0)

    return df


def calculate_returns_portfolio(pos_df):
    pos_df = calculate_portfolio_daily_returns(pos_df)

    portfolio_df = calculate_portfolio_acc_return(pos_df)
    category_df = calculate_category_acc_return(pos_df)
    assets_df = calculate_asset_acc_returns(pos_df)

    category_df = portfolio_df.merge(category_df, on='date', how='left')
    
    return {
        "assets_returns": assets_df,
        "category_returns": category_df
    }
    
def calculate_portfolio_acc_return(df):
    df = df.copy()
    df['weighted_return'] = (df['value'] / df['net_value_day']) * df['asset_return']
    grouped = df.groupby('date')['weighted_return'].sum().reset_index()
    grouped['portfolio'] = (1 + grouped['weighted_return']).cumprod() - 1
    return grouped.drop(columns='weighted_return')


def calculate_category_acc_return(df):
    df = df.copy()

    df['category_total_value'] = df.groupby(['date', 'category'])['value'].transform('sum')
    df['category_weight'] = df['value'] / df['category_total_value']
    df['category_weighted_return'] = df['category_weight'] * df['asset_return']

    grouped = df.groupby(['date', 'category'])['category_weighted_return'].sum().reset_index()
    pivot = grouped.pivot(index='date', columns='category', values='category_weighted_return')
    cumulative = (1 + pivot.fillna(0)).cumprod() - 1
    return cumulative.reset_index()

def calculate_asset_acc_returns(df):
    df = df.copy()
    df = df.sort_values(['ticker', 'date'])
    df['asset_cum_return'] = (1 + df['asset_return']).groupby(df['ticker']).cumprod() - 1
    df.loc[df['quantity'] == 0, 'asset_cum_return'] = None
    pivot = df.pivot(index='date', columns='ticker', values='asset_cum_return')
    return pivot.reset_index()

def calculate_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change().fillna(0)

def calculate_acc_returns(returns: pd.Series) -> pd.Series:
    return (1 + returns).cumprod() - 1

def calculate_acc_returns_from_prices(prices: pd.Series) -> pd.Series:
    return prices / prices.iloc[0] - 1