import pandas as pd


class TesouroClient:
    def __init__(self):
        pass

    @staticmethod
    def get_taxas_precos_tesouro():
        try:
            taxas_precos_history_url = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'
            data = pd.read_csv(taxas_precos_history_url, sep=';', decimal=',')
            data['Data Base'] = pd.to_datetime(data['Data Base'], format='%d/%m/%Y', dayfirst=True)
            data['Data Vencimento'] = pd.to_datetime(
                data['Data Vencimento'], format='%d/%m/%Y', dayfirst=True
            )
            return data
        except Exception:
            return None

    def get_precos_tesouro(self, tipo_titulo, vencimento):
        taxas_precos_df = self.get_taxas_precos_tesouro()
        df = taxas_precos_df[taxas_precos_df['Tipo Titulo'] == tipo_titulo]
        df = df[df['Data Vencimento'] == pd.to_datetime(vencimento)]
        df = df.sort_values(by='Data Base').rename(
            columns={
                'Taxa Compra Manha': 'fee',
                'PU Venda Manha': 'price',
                'Data Base': 'date',
            }
        )
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', dayfirst=True)
        df = df.set_index('date').asfreq('D')
        df['close'] = df['price'].ffill().copy()
        df = df.reset_index()
        df['currency'] = 'BRL'
        return df[['date', 'close', 'currency']]
    
    def get_quotes(
        self, 
        treasury_type,
        treasury_maturity_date,
        start_date = None,
        end_date = None,        
        ):
        
        history_df = self.get_precos_tesouro(treasury_type, treasury_maturity_date)
        
        if start_date:
            history_df = history_df[history_df['date'] >= pd.to_datetime(start_date).normalize()]
        if end_date:
            history_df = history_df[history_df['date'] <= pd.to_datetime(end_date).normalize()]
        
        return {
            'currency': 'BRL',
            'quotes': history_df[['date', 'close']], 
        }
