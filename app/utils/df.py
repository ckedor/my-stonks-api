import pandas as pd


def df_to_named_dict(df: pd.DataFrame) -> dict[str, list[dict]]:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return {
        col: df[['date', col]]
        .dropna()
        .rename(columns={col: 'value'})
        .to_dict(orient='records')
        for col in df.columns
        if col != 'date'
    }