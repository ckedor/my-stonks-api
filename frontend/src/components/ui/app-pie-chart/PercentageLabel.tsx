
import { useTheme } from '@mui/material'
import { PieLabelRenderProps } from 'recharts'

export default function PercentageLabel({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
}: PieLabelRenderProps) {
  const theme = useTheme()
  
  const RADIAN = Math.PI / 180
  const radius = Number(innerRadius) + (Number(outerRadius) - Number(innerRadius)) * 0.5
  const angle = Number(midAngle)
  const x = Number(cx) + radius * Math.cos(-angle * RADIAN)
  const y = Number(cy) + radius * Math.sin(-angle * RADIAN)

  return (
    <text
      x={x}
      y={y}
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={12}
      style={{ pointerEvents: 'none', fill: theme.palette.dark }}
    >
      {`${(Number(percent) * 100).toFixed(1)}%`}
    </text>
  )
}
