import pandas as pd


class ReturnsCalculator:
    def __init__(self):
        pass

    def calculate_returns_portfolio(self, pos_df):
        pos_df = pos_df.copy()
        pos_df['date'] = pd.to_datetime(pos_df['date'])
        pos_df = pos_df.sort_values(['date', 'asset_id'])

        pos_df['value'] = pos_df['quantity'] * pos_df['price']
        pos_df['contribution'] = (
            pos_df.groupby('asset_id')['quantity'].diff().fillna(0) * pos_df['price']
        )
        pos_df['net_value_day'] = pos_df.groupby('date')['value'].transform('sum') - pos_df.groupby(
            'date'
        )['contribution'].transform('sum')

        pos_df['asset_return'] = pos_df.groupby('asset_id')['price'].pct_change()
        base_valor = pos_df['value'] - pos_df['contribution']
        pos_df['asset_return'] += pos_df['dividend'] / base_valor.replace(0, pd.NA)
        pos_df['asset_return'] = pos_df['asset_return'].fillna(0)

        portfolio_df = self._calculate_portfolio_return(pos_df)
        category_df = self._calculate_category_return(pos_df)
        assets_df = self.calculate_asset_returns(pos_df)

        category_df = portfolio_df.merge(category_df, on='date', how='left')
        
        return {
            "assets_returns": assets_df,
            "category_returns": category_df
        }

    @staticmethod
    def _calculate_portfolio_return(df):
        df = df.copy()
        df['weighted_return'] = (df['value'] / df['net_value_day']) * df['asset_return']
        grouped = df.groupby('date')['weighted_return'].sum().reset_index()
        grouped['portfolio'] = (1 + grouped['weighted_return']).cumprod() - 1
        return grouped.drop(columns='weighted_return')

    @staticmethod
    def _calculate_category_return(df):
        df = df.copy()

        df['category_total_value'] = df.groupby(['date', 'category'])['value'].transform('sum')
        df['category_weight'] = df['value'] / df['category_total_value']
        df['category_weighted_return'] = df['category_weight'] * df['asset_return']

        grouped = df.groupby(['date', 'category'])['category_weighted_return'].sum().reset_index()
        pivot = grouped.pivot(index='date', columns='category', values='category_weighted_return')
        cumulative = (1 + pivot.fillna(0)).cumprod() - 1
        return cumulative.reset_index()

    @staticmethod
    def calculate_asset_returns(pos_df):
        pos_df = pos_df.copy()
        pos_df['date'] = pd.to_datetime(pos_df['date'])
        pos_df = pos_df.sort_values(['date', 'asset_id'])

        pos_df['value'] = pos_df['quantity'] * pos_df['price']
        pos_df['contribution'] = (
            pos_df.groupby('asset_id')['quantity'].diff().fillna(0) * pos_df['price']
        )
        pos_df['net_value_day'] = pos_df.groupby('date')['value'].transform('sum') - pos_df.groupby(
            'date'
        )['contribution'].transform('sum')

        pos_df['asset_return'] = pos_df.groupby('asset_id')['price'].pct_change()
        base_valor = pos_df['value'] - pos_df['contribution']
        pos_df['asset_return'] += pos_df['dividend'] / base_valor.replace(0, pd.NA)
        pos_df['asset_return'] = pos_df['asset_return'].fillna(0)

        pos_df = pos_df.sort_values(['ticker', 'date'])
        pos_df['asset_cum_return'] = (1 + pos_df['asset_return']).groupby(
            pos_df['ticker']
        ).cumprod() - 1
        pos_df.loc[pos_df['quantity'] == 0, 'asset_cum_return'] = None
        pivot = pos_df.pivot(index='date', columns='ticker', values='asset_cum_return')
        return pivot.reset_index()

    @staticmethod
    def calculate_acc_returns(series: pd.Series) -> pd.Series:
        return series / series.iloc[0] - 1
