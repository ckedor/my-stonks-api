
import { login } from '@/actions/auth'
import { loginRequest } from '@/lib/api'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    IconButton,
    InputAdornment,
    Link,
    Snackbar,
    TextField,
    Typography,
} from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const [errorOpen, setErrorOpen] = useState(false)

  const handleSubmit = async () => {
    if (loading) return
    setLoading(true)
    try {
      const { access_token } = await loginRequest(username, password)
      await login(access_token)
      navigate('/portfolio/overview')
    } catch (err) {
      console.log(err)
      setErrorOpen(true)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {/* Left side — image */}
        <Box
          sx={{
            display: { xs: 'none', md: 'block' },
            width: '45%',
            backgroundImage: 'url(/home.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        {/* Right side — form */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'background.default',
            px: 3,
          }}
        >
          <Box sx={{ width: '100%', maxWidth: 480 }}>
            <Typography variant="h3" fontWeight={700} gutterBottom>
              Acesse sua conta
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 5 }}>
              Bem-vindo ao My Stonks. Faça login para continuar.
            </Typography>

            <Typography variant="body1" fontWeight={500} sx={{ mb: 0.5 }}>
              E-mail
            </Typography>
            <TextField
              fullWidth
              placeholder="seu@email.com"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
              sx={{ mb: 3 }}
            />

            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
              <Typography variant="body1" fontWeight={500}>
                Senha
              </Typography>
              <Link href="#" variant="body2" underline="hover" color="primary">
                Esqueci minha senha
              </Link>
            </Box>
            <TextField
              fullWidth
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={() => setShowPassword((v) => !v)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
              sx={{ mb: 4 }}
            />

            <Button
              variant="contained"
              fullWidth
              size="large"
              onClick={handleSubmit}
              disabled={loading}
              sx={{ py: 1.5, fontWeight: 600, fontSize: '1.05rem' }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Acessar conta'}
            </Button>
          </Box>
        </Box>
      </Box>

      <Snackbar
        open={errorOpen}
        autoHideDuration={4000}
        onClose={() => setErrorOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setErrorOpen(false)}>
          Usuário ou senha inválidos
        </Alert>
      </Snackbar>
    </>
  )
}
