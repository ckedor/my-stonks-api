import { Card, CardContent, Grid } from '@mui/material'
import InformationCardField, { InformationCardFieldProps } from './InformationCardField'

type InformationCardProps = {
  fields: InformationCardFieldProps[]
}

export default function InformationCard({ fields }: InformationCardProps) {
  return (
    <Card>
      <CardContent sx={{ margin: 0, padding: 2 }}>
        <Grid container spacing={3}>
          {fields.map((field, index) => (
            <InformationCardField key={index} {...field} />
          ))}
        </Grid>
      </CardContent>
    </Card>
  )
}
