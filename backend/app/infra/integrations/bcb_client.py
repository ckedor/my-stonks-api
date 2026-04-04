# app/infra/integrations/bcb_client.py
from datetime import datetime

import pandas as pd

from app.infra.http import AsyncHttpClient


class BCBClient:
    def __init__(self):
        self.index_endpoints = {
            'CDI': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json',
            'IPCA': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json',
            'USD/BRL': 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo',
        }
        self.http = AsyncHttpClient(
            timeout=30.0,
            max_retries=3,
            backoff_factor=1.0,
        )

    async def get_usd_brl_quotation(self, init_date: pd.Timestamp = None):
        try:
            data_inicial_str = init_date.strftime('%m-%d-%Y') if init_date else '01-01-1970'
            data_final_str = datetime.now().strftime('%m-%d-%Y')

            params = (
                f'(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)'
                f"?@dataInicial='{data_inicial_str}'&@dataFinalCotacao='{data_final_str}'"
                f'&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao'
            )

            endpoint = self.index_endpoints['USD/BRL'] + params
            response = await self.http.get(endpoint)

            quotations = response['value']
            df = pd.DataFrame(quotations)
            df = df.rename(columns={'cotacaoCompra': 'value', 'dataHoraCotacao': 'date'})[
                ['value', 'date']
            ]

            df['date'] = pd.to_datetime(df['date']).dt.normalize()
            df = df.sort_values('date').drop_duplicates(subset='date', keep='last')

            full_range = pd.date_range(df['date'].min(), df['date'].max(), freq='D')
            df = df.set_index('date').reindex(full_range).rename_axis('date').ffill().reset_index()

            return df

        except Exception as e:
            raise Exception(
                f'Erro ao buscar dados da API do BCB: Cotação USD/BRL. Erro: {str(e)}'
            ) from e

    async def get_market_index_history_df(
        self, index_name: str, init_date: pd.Timestamp = None
    ) -> pd.DataFrame:
        try:
            if index_name.upper() not in self.index_endpoints:
                raise ValueError(f"Índice '{index_name}' não suportado.")

            endpoint = self.index_endpoints[index_name.upper()]

            if init_date:
                from_date = init_date - pd.DateOffset(
                    months=2
                )  # o bcb dá erro no IPCA se não vem valor então no minimo 2 meses de janela
                endpoint += f'&dataInicial={from_date.strftime("%d/%m/%Y")}'
            else:
                from_date = datetime.today() - pd.DateOffset(years=10)
                endpoint += f'&dataInicial={from_date.strftime("%d/%m/%Y")}'

            data = await self.http.get(endpoint)
            df = pd.DataFrame(data)
            df['value'] = df['valor'].str.replace(',', '.').astype(float)
            df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

            return df[['date', 'value']]

        except Exception as e:
            raise Exception(
                f'Erro ao buscar dados da API do BCB. Índice: {index_name.upper()}. Erro: {str(e)}'
            ) from e

    async def close(self):
        """Close the HTTP client."""
        await self.http.close()
