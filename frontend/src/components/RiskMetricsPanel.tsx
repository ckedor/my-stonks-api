import { AssetAnalysis } from '@/types';
import { Box, Divider, Typography } from '@mui/material';

interface Props {
  analysis: AssetAnalysis
}

function MetricRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={600} color={color ?? 'text.primary'}>
        {value}
      </Typography>
    </Box>
  )
}

export default function RiskMetricsPanel({ analysis }: Props) {
  const { risk_metrics } = analysis

  return (
    <Box>
      <Typography variant="subtitle2" fontWeight={600} mb={1}>
        Métricas de Risco
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
        <Box>
          <MetricRow
            label="Volatilidade Anual"
            value={`${(risk_metrics.annualized_vol * 100).toFixed(2)}%`}
          />
          <MetricRow
            label="Sharpe Ratio"
            value={risk_metrics.sharpe_ratio.toFixed(3)}
            color={risk_metrics.sharpe_ratio > 0 ? 'success.main' : 'error.main'}
          />
          <MetricRow
            label="Max Drawdown"
            value={`${(risk_metrics.drawdown.stats.max_drawdown * 100).toFixed(2)}%`}
            color="error.main"
          />
          <MetricRow
            label="Semidesvio"
            value={`${(risk_metrics.semideviation * 100).toFixed(4)}%`}
          />
        </Box>

        <Box>
          <MetricRow
            label="VaR 95%"
            value={`${(risk_metrics.var_95 * 100).toFixed(2)}%`}
            color="warning.main"
          />
          <MetricRow
            label="CVaR 95%"
            value={`${(risk_metrics.cvar_95 * 100).toFixed(2)}%`}
            color="warning.main"
          />
          <MetricRow
            label="Assimetria"
            value={risk_metrics.skewness.toFixed(3)}
          />
          <MetricRow
            label="Curtose"
            value={risk_metrics.kurtosis.toFixed(2)}
          />
        </Box>
      </Box>

      <Divider sx={{ my: 2 }} />
    </Box>
  )
}
