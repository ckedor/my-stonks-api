import { Box, Paper, Typography } from '@mui/material'

export default function AdminUsersPage() {

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Gerenciamento de Usuários
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Área para gerenciar os usuários do sistema.
        </Typography>
        <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
          Em desenvolvimento...
        </Typography>
      </Paper>
    </Box>
  )
}
