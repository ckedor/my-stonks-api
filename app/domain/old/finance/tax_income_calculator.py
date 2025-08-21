import pandas as pd

from app.domain.income_tax.constants import (
    FREE_TAX_LIMIT_CRYPTO,
    FREE_TAX_LIMIT_STOCK,
    TAX_RATE_CRYPTO,
    TAX_RATE_ETF,
    TAX_RATE_FII,
    TAX_RATE_STOCK,
)


class TaxIncomeCalculator:
    def __init__(self, tax_rate: float, free_tax_limit: float = 0.0):
        self.tax_rate = tax_rate
        self.free_tax_limit = free_tax_limit
    
    def calculate_tax(self, df: pd.DataFrame) -> pd.DataFrame:
        acc_loss = 0.0

        for idx, row in df.iterrows():
            profit = row['realized_profit']
            total_sold = row['gross_sales']
            tax_due = 0.0

            if profit < 0:
                acc_loss += -profit
            else:
                profit_after_loss = profit - acc_loss

                if self.free_tax_limit and total_sold <= self.free_tax_limit:
                    tax_due = 0.0
                elif profit_after_loss <= 0:
                    acc_loss -= profit
                else:
                    tax_due = profit_after_loss * self.tax_rate
                    acc_loss = 0.0

            df.at[idx, 'accumulated_loss'] = acc_loss
            df.at[idx, 'tax_due'] = round(tax_due, 2)

        return df

class FIITaxCalculator(TaxIncomeCalculator):
    def __init__(self):
        super().__init__(tax_rate=TAX_RATE_FII)

class ETFTaxCalculator(TaxIncomeCalculator):
    def __init__(self):
        super().__init__(tax_rate=TAX_RATE_ETF)

class BRStockTaxCalculator(TaxIncomeCalculator):
    def __init__(self):
        super().__init__(tax_rate=TAX_RATE_STOCK, free_tax_limit=FREE_TAX_LIMIT_STOCK)

class CryptoTaxCalculator(TaxIncomeCalculator):
    def __init__(self):
        super().__init__(tax_rate=TAX_RATE_CRYPTO, free_tax_limit=FREE_TAX_LIMIT_CRYPTO)
