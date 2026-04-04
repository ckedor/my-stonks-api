import { DateRangeKey } from "@/lib/utils/date"
import { Stack, Typography } from "@mui/material"

export interface RangeOption {
  label: string
  value: DateRangeKey
}


export default function DateRangeMenu({
  show,
  range,
  options,
  onChange,
}: {
  show: boolean
  range: DateRangeKey
  options: RangeOption[]
  onChange: (v: DateRangeKey) => void
}) {

    const fontSize = 13

    if (!show) return null

    return (
        <Stack direction="row" spacing={1}>
        {options.map((r) => (
            <Typography
            key={r.value}
            onClick={() => onChange(r.value)}
            sx={{
                cursor: 'pointer',
                fontWeight: range === r.value ? 700 : 400,
                fontSize: {fontSize},
            }}
            >
            {r.label}
            </Typography>
        ))}
        </Stack>
    )
}