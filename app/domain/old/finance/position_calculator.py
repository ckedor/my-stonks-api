import pandas as pd


class PositionCalculator:
    
    @staticmethod
    def calculate_monthly_profits(trades_df: pd.DataFrame) -> pd.DataFrame:
        required_columns = {"date", "quantity", "price", "total_amount"}
        missing = required_columns - set(trades_df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        df = PositionCalculator.calculate_profits(trades_df)
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        df['gross_sales'] = df.apply(
            lambda row: -row['total_amount'] if row['quantity'] < 0 else 0.0, axis=1
        )

        monthly_profits = df.groupby('month').agg({
            'realized_profit': 'sum',
            'gross_sales': 'sum'
        }).reset_index()

        return monthly_profits

    @staticmethod
    def calculate_profits(trades_df: pd.DataFrame) -> pd.DataFrame:
        trades_df = trades_df.sort_values(by='date').reset_index(drop=True)
        df = trades_df.copy()
        realized_profits = []
        average_prices = []

        quantity_held = 0.0
        total_cost = 0.0

        for _, row in df.iterrows():
            quantity = row['quantity']
            price = row['price']
            is_buy = quantity > 0
            realized_profit = 0.0

            avg_price = total_cost / quantity_held if quantity_held else 0

            if is_buy:
                total_cost += quantity * price
                quantity_held += quantity
            else:
                realized_profit = abs(quantity) * (price - avg_price)
                total_cost -= avg_price * abs(quantity)
                quantity_held += quantity

            avg_price = total_cost / quantity_held if quantity_held else 0
            realized_profits.append(realized_profit)
            average_prices.append(avg_price)

        df['realized_profit'] = realized_profits
        df['average_price'] = average_prices
        return df