import pandas as pd

from app.domain.finance.performance_metrics import (
    annualize_rets,
    annualize_vol,
    sharpe_ratio,
)
from app.domain.finance.returns import calculate_returns
from app.domain.finance.risk_metrics import (
    cvar_historic,
    drawdown,
    drawdown_stats,
    kurtosis,
    semideviation,
    skewness,
    var_historic,
)


def calculate_asset_analysis(
    asset_returns: pd.Series,
    benchmarks: dict[str, pd.Series],
) -> dict:
    
    cdi_returns = calculate_returns(benchmarks['CDI'])
    
    return {
        "start_date": asset_returns.index.min().strftime('%Y-%m-%d'),
        "performance_metrics": calculate_performance_metrics(asset_returns, benchmarks),
        "risk_metrics": calculate_risk_metrics(asset_returns, cdi_returns),
        "rolling_cagr": _calculate_rolling_12m(asset_returns),
    }


def _calculate_rolling_12m(asset_returns: pd.Series) -> list[dict]:
    """Calculate rolling 12-month return from daily returns and serialize."""
    acc = (1 + asset_returns).cumprod()
    acc_12m_ago = acc.shift(365)
    rolling_12m = (acc / acc_12m_ago - 1).dropna()
    return [
        {"date": str(date.date()), "value": float(val) * 100}
        for date, val in rolling_12m.items()
    ]


def calculate_risk_metrics(asset_returns, cdi_returns):
    annual_vol = annualize_vol(asset_returns)
    sr = sharpe_ratio(asset_returns, cdi_returns)

    dd_df = drawdown(asset_returns)
    dd_stats = drawdown_stats(asset_returns)

    dd_serialized = (
        dd_df["drawdown"]
        .reset_index()
        .rename(columns={"index": "date"})
    )
    dd_serialized["date"] = dd_serialized["date"].astype(str)
    dd_serialized = dd_serialized.to_dict(orient="records")

    return {
        "annualized_vol": annual_vol,
        "sharpe_ratio": sr,
        "drawdown": {
            "series": dd_serialized,
            "stats": dd_stats,
        },
        "semideviation": semideviation(asset_returns),
        "skewness": skewness(asset_returns),
        "kurtosis": kurtosis(asset_returns),
        "var_95": var_historic(asset_returns, level=5),
        "cvar_95": cvar_historic(asset_returns, level=5),
    }

def calculate_performance_metrics(asset_returns, benchmarks):
    cagr = annualize_rets(asset_returns)
    
    benchmarks_metrics = {}
    for name, benchmark_history in benchmarks.items():
        benchmark_returns = calculate_returns(benchmark_history)
        cagr_benchmark = annualize_rets(benchmark_returns)
        alpha = cagr - cagr_benchmark
        
        corr = asset_returns.corr(benchmark_returns)
        beta = corr * (asset_returns.std() / benchmark_returns.std()) if benchmark_returns.std() > 0 else 0
        benchmarks_metrics[name] = {
            "cagr": cagr_benchmark * 100,
            "alpha": alpha * 100,
            "beta": beta,
            "correlation": corr
        }

    return{
        "cagr": cagr * 100,
        "benchmarks_metrics": benchmarks_metrics
    }