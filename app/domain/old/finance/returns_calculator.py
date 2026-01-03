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
    def _calculate_category_return(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['asset_id', 'date'])

        # Garanta que estes campos existem (no seu pipeline eles já existem)
        # value = quantity * price
        # contribution = diff(quantity) * price
        # asset_return = pct_change(price) + dividend/base_valor

        df['base_value'] = (df['value'] - df['contribution']).replace(0, pd.NA)

        # Peso do início do período: valor pré-fluxo de t-1
        df['base_value_prev'] = df.groupby('asset_id')['base_value'].shift(1)

        # Total da categoria no início do período (t-1)
        df['category_base_prev_total'] = df.groupby(['date', 'category'])['base_value_prev'].transform('sum')

        # Se a categoria ainda não existia em t-1 (NaN/0), evita divisão por zero
        df['category_weight'] = df['base_value_prev'] / df['category_base_prev_total'].replace(0, pd.NA)
        df['category_weight'] = df['category_weight'].fillna(0)

        df['category_weighted_return'] = df['category_weight'] * df['asset_return']

        daily = df.groupby(['date', 'category'])['category_weighted_return'].sum().reset_index()
        pivot = daily.pivot(index='date', columns='category', values='category_weighted_return').fillna(0)

        cumulative = (1 + pivot).cumprod() - 1
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
