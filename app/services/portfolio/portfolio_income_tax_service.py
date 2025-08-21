import pandas as pd

from app.infrastructure.db.models.constants.asset_type import ASSET_TYPE
from app.infrastructure.db.models.constants.currency import CURRENCY
from app.infrastructure.db.repositories.portfolio import PortfolioRepository
from app.utils.response import df_response


async def get_assets_and_rights(session, portfolio_id: int, fiscal_year: int) -> dict:
    repo = PortfolioRepository(session)
    last_day_fiscal_year = pd.to_datetime(f'{fiscal_year}-12-31')
    last_day_previous_year = pd.to_datetime(f'{fiscal_year - 1}-12-31')

    position_dec_fy = await repo.get_position_on_date(portfolio_id, last_day_fiscal_year)
    position_dec_prev = await repo.get_position_on_date(portfolio_id, last_day_previous_year)

    df = pd.merge(
        position_dec_fy,
        position_dec_prev,
        on=['asset_id', 'ticker'],
        how='outer',
        suffixes=('_fiscal_year', '_previous_year'),
    )

    df['type_id'] = df['type_id_fiscal_year'].combine_first(df['type_id_previous_year'])
    df['class'] = df['class_fiscal_year'].combine_first(df['class_previous_year'])
    df['category'] = df['category_fiscal_year'].combine_first(df['category_previous_year'])
    df['currency_id'] = df['currency_id_fiscal_year'].combine_first(df['currency_id_previous_year'])
    df['name'] = df['name_fiscal_year'].combine_first(df['name_previous_year'])

    df['price_fiscal_year'] = df['price_fiscal_year'].fillna(0.0)
    df['price_previous_year'] = df['price_previous_year'].fillna(0.0)
    df['quantity_fiscal_year'] = df['quantity_fiscal_year'].fillna(0.0)
    df['quantity_previous_year'] = df['quantity_previous_year'].fillna(0.0)

    df['position_fiscal_year'] = df['quantity_fiscal_year'] * df['price_fiscal_year']
    df['position_previous_year'] = df['quantity_previous_year'] * df['price_previous_year']
    
    df['position_previous_year'] = df['position_previous_year'].round(2)
    df['position_fiscal_year'] = df['position_fiscal_year'].round(2)

    # Exclui previdência (PGBL)
    df = df[df['type_id'] != ASSET_TYPE.PREV]

    df['grupo'] = df.apply(_map_group, axis=1)
    df['codigo'] = df.apply(_map_code, axis=1)
    df['discriminacao'] = df.apply(_map_description, axis=1)
    df['codigo_negociacao'] = df['ticker']
    df['negociado_em_bolsa'] = df['type_id'].apply(_is_traded_on_exchange)
    df['locale'] = df.apply(_map_locale, axis=1)
    df['cnpj'] = '02.332.886/0001-04' # TODO: Agrupar posição por corretora

    final_df = df[[
        'grupo', 'codigo', 'discriminacao',
        'position_previous_year', 'position_fiscal_year',
        'codigo_negociacao', 'negociado_em_bolsa', 'locale', 'cnpj'
    ]]

    return df_response(final_df)

def _is_traded_on_exchange(asset_type):
    return asset_type in {
        ASSET_TYPE.ETF, ASSET_TYPE.FII, ASSET_TYPE.STOCK, ASSET_TYPE.BDR, ASSET_TYPE.FI
    }
    
def _map_locale(row):
    if row['type_id'] == ASSET_TYPE.CRIPTO:
        return '105'  # Cripto no Brasil
    return '249' if row['currency_id'] == CURRENCY.USD else '105'

def _map_group(row):
    if row['type_id'] == ASSET_TYPE.CRIPTO:
        return '08'
    elif row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.BRL:
        return '03'  # Ações brasileiras
    elif row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.USD:
        return '04'  # Ações no exterior
    elif row['type_id'] == ASSET_TYPE.ETF and row['currency_id'] == CURRENCY.USD:
        return '04'  # ETF exterior
    elif row['type_id'] in [ASSET_TYPE.ETF, ASSET_TYPE.FII, ASSET_TYPE.FI]:
        return '07'
    elif row['type_id'] in [
        ASSET_TYPE.CDB, ASSET_TYPE.CRA, ASSET_TYPE.CRI,
        ASSET_TYPE.DEB, ASSET_TYPE.TREASURY, ASSET_TYPE.BDR
    ]:
        return '04'
    else:
        return '99'

def _map_code(row):
    if row['type_id'] == ASSET_TYPE.CRIPTO:
        if row['ticker'] == 'BTC':
            return '01'
        elif row['ticker'] in ['ETH', 'ADA', 'SOL', 'XRP']:
            return '02'
        elif row['ticker'] in ['USDT', 'USDC', 'DAI']:
            return '03'
        else:
            return '99'

    if row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.BRL:
        return '01'
    if row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.USD:
        return '99'
    if row['type_id'] == ASSET_TYPE.ETF and row['currency_id'] == CURRENCY.USD:
        return '99'

    elif row['type_id'] in [ASSET_TYPE.CDB, ASSET_TYPE.DEB, ASSET_TYPE.TREASURY]:
        return '02'
    elif row['type_id'] in [ASSET_TYPE.CRA, ASSET_TYPE.CRI]:
        return '03'
    elif row['type_id'] == ASSET_TYPE.BDR:
        return '04'
    elif row['type_id'] == ASSET_TYPE.FII:
        return '03'
    elif row['type_id'] == ASSET_TYPE.ETF:
        return '09'
    elif row['type_id'] == ASSET_TYPE.FI:
        return '13'
    else:
        return '99'

def _map_description(row):
    if row['type_id'] == ASSET_TYPE.CRIPTO:
        return f"Criptoativo {row['name']} ({row['ticker']}), armazenado em exchange nacional."
    if row['type_id'] == ASSET_TYPE.CDB:
        return f"CDB {row['name']} ({row['ticker']}), adquirido via corretora brasileira."
    if row['type_id'] == ASSET_TYPE.TREASURY:
        return f"Título público {row['name']} ({row['ticker']}), adquirido via Tesouro Direto."
    if row['type_id'] == ASSET_TYPE.CRA:
        return f"CRA {row['name']} ({row['ticker']}), isento de IR, adquirido via corretora brasileira."
    if row['type_id'] == ASSET_TYPE.CRI:
        return f"CRI {row['name']} ({row['ticker']}), isento de IR, adquirido via corretora brasileira."
    if row['type_id'] == ASSET_TYPE.DEB:
        return f"Debênture {row['name']} ({row['ticker']}), adquirida via corretora brasileira."
    if row['type_id'] == ASSET_TYPE.ETF and row['currency_id'] == CURRENCY.BRL:
        return f"ETF {row['name']} ({row['ticker']}) negociado na B3."
    if row['type_id'] == ASSET_TYPE.ETF and row['currency_id'] == CURRENCY.USD:
        return f"ETF {row['name']} ({row['ticker']}) negociado no exterior."
    if row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.BRL:
        return f"Ações da empresa {row['name']} ({row['ticker']}) negociadas na B3."
    if row['type_id'] == ASSET_TYPE.STOCK and row['currency_id'] == CURRENCY.USD:
        return f"Ações da empresa {row['name']} ({row['ticker']}) negociadas no exterior."
    if row['type_id'] == ASSET_TYPE.BDR:
        return f"BDR da empresa {row['name']} ({row['ticker']}), negociado na B3."
    if row['type_id'] == ASSET_TYPE.FII:
        return f"Fundo Imobiliário {row['name']} ({row['ticker']}) negociado na B3."
    if row['type_id'] == ASSET_TYPE.FI:
        return f"Fundo de investimento {row['name']} ({row['ticker']}) com tributação periódica."
    else:
        return f"Ativo {row['name']} ({row['ticker']})"

async def get_fiis_operations_tax(session, portfolio_id: int, fiscal_year: int) -> dict:
    repo = PortfolioRepository(session)
    df = await repo.get_transactions_df(portfolio_id, asset_types_ids=[ASSET_TYPE.FII])
    response =  await _get_operations_tax(df, fiscal_year, FIITaxCalculator())
    return df_response(response)

async def get_common_operations_tax(session, portfolio_id: int, fiscal_year: int) -> dict:
    repo = PortfolioRepository(session)
    br_stocks_df = await repo.get_transactions_df(
        portfolio_id,
        asset_types_ids=[ASSET_TYPE.STOCK],
        currency_id=CURRENCY.BRL
    )
    br_result = await _get_operations_tax(br_stocks_df, fiscal_year, BRStockTaxCalculator())
    
    br_etf_bdr_df = await repo.get_transactions_df(
        portfolio_id,
        asset_types_ids=[ASSET_TYPE.ETF, ASSET_TYPE.BDR],
        currency_id=CURRENCY.BRL
    )
    br_etf_bdr_result = await _get_operations_tax(br_etf_bdr_df, fiscal_year, ETFTaxCalculator())

    merged = pd.concat([br_result, br_etf_bdr_result], ignore_index=True)
    grouped = merged.groupby('month', as_index=False).agg({
        'realized_profit': 'sum',
        'accumulated_loss': 'sum',
        'tax_due': 'sum',
    })

    return df_response(grouped)

#cripto_df = await repo.get_transactions_df(
#        portfolio_id,
#        asset_types_ids=[ASSET_TYPE.CRIPTO]
#    )
#    cripto_result = await _get_operations_tax(cripto_df, fiscal_year, CryptoTaxCalculator())
#
#    etfs_bdrs_df = await repo.get_transactions_df(
#        portfolio_id,
#        asset_types_ids=[ASSET_TYPE.ETF, ASSET_TYPE.BDR],
#    )
#    usa_stocks_df = await repo.get_transactions_df(
#        portfolio_id,
#        asset_types_ids=[ASSET_TYPE.STOCK],
#        currency_id=CURRENCY.USD
#    )
#    variable_income_df = pd.concat([etfs_bdrs_df, usa_stocks_df], ignore_index=True)
#    variable_income_result = await _get_operations_tax(variable_income_df, fiscal_year, ETFTaxCalculator())

async def _get_operations_tax(df: pd.DataFrame, fiscal_year: int, tax_calculator) -> dict:
    df['total_amount'] = df['quantity'] * df['price']
    df = _calculate_monthly_profits(df)

    taxed_df = tax_calculator.calculate_tax(df)

    last_day_fiscal_year = pd.to_datetime(f"{fiscal_year}-12-31")
    last_day_previous_year = pd.to_datetime(f"{fiscal_year - 1}-12-31")
    all_months = pd.date_range(
        start=last_day_previous_year + pd.offsets.MonthBegin(1),
        end=last_day_fiscal_year,
        freq='MS'
    ).to_period('M')

    full_months_df = pd.DataFrame({'month': all_months})
    taxed_df = full_months_df.merge(taxed_df, on='month', how='left')
    taxed_df['realized_profit'] = taxed_df['realized_profit'].fillna(0.0)
    taxed_df['accumulated_loss'] = taxed_df['accumulated_loss'].ffill().fillna(0.0)
    taxed_df['tax_due'] = taxed_df['tax_due'].fillna(0.0)
    taxed_df['month'] = taxed_df['month'].astype(str)

    return taxed_df

@staticmethod
def _calculate_monthly_profits(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(by=['asset_id', 'date']).copy()

    results = []
    for _, group in df.groupby('asset_id'):
        result = PositionCalculator.calculate_monthly_profits(group)
        results.append(result)

    result = pd.concat(results).sort_index()
    monthly_df = result.groupby('month').agg(
        realized_profit=('realized_profit', 'sum'),
        gross_sales=('gross_sales', 'sum')
    ).reset_index()
    
    return monthly_df

async def get_darf(session, portfolio_id: int, fiscal_year: int) -> dict:
    repo = PortfolioRepository(session)
    
    cripto_transactions_df = await repo.get_transactions_df(
        portfolio_id,
        asset_types_ids=[ASSET_TYPE.CRIPTO]
    )
    cripto_taxes_df = await _get_operations_tax(cripto_transactions_df, fiscal_year, CryptoTaxCalculator())
    cripto_taxes_df['label'] = 'Criptomoedas (Brasil)'
    
    fiis_transactions_df = await repo.get_transactions_df(portfolio_id, asset_types_ids=[ASSET_TYPE.FII])
    fiis_taxes_df = await _get_operations_tax(fiis_transactions_df, fiscal_year, FIITaxCalculator())
    fiis_taxes_df['label'] = 'FII'
    
    br_stocks_transactions_df = await repo.get_transactions_df(
        portfolio_id,
        asset_types_ids=[ASSET_TYPE.STOCK],
        currency_id=CURRENCY.BRL
    )
    br_stocks_taxes_df = await _get_operations_tax(br_stocks_transactions_df, fiscal_year, BRStockTaxCalculator())
    br_stocks_taxes_df['label'] = 'Bolsa (Brasil)'
    
    etf_bdr_transactions_df = await repo.get_transactions_df(
        portfolio_id,
        asset_types_ids=[ASSET_TYPE.ETF, ASSET_TYPE.BDR],
        currency_id=CURRENCY.BRL
    )
    etf_bdr_taxes_df = await _get_operations_tax(etf_bdr_transactions_df, fiscal_year, ETFTaxCalculator())
    etf_bdr_taxes_df['label'] = 'Bolsa (Brasil)'
    
    
    combined = pd.concat([
        br_stocks_taxes_df,
        fiis_taxes_df,
        etf_bdr_taxes_df,
        cripto_taxes_df,
    ], ignore_index=True)
    
    grouped = combined.groupby(['month', 'label'], as_index=False).agg({
        'realized_profit': 'sum',
        'tax_due': 'sum'
    })
    
    result = []
    for month, group in grouped.groupby('month'):
        entries = []
        for _, row in group.iterrows():
            entries.append({
                'label': row['label'],
                'base': row['realized_profit'],
                'tax': row['tax_due'],
                'darf': row['tax_due'],
            })
        result.append({
            'month': month,
            'entries': entries
        })

    return result
    
        
