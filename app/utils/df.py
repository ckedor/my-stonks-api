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
    
def extend_values_to_today(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.sort_values("date").reset_index(drop=True)

    last_date = df["date"].max()
    today = pd.Timestamp.today().normalize()

    if last_date >= today:
        return df

    full_range = pd.date_range(start=df["date"].min(), end=today, freq="D")

    df = df.set_index("date").reindex(full_range)

    df = df.ffill()
    df = df.rename_axis("date").reset_index()

    return df
