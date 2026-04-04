
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { Button, ButtonProps } from '@mui/material'
import { styled } from '@mui/material/styles'
import { useNavigate } from 'react-router-dom'

const BackButtonRoot = styled(Button)(({ theme }) => ({
  textTransform: 'none',
  fontWeight: 500,
  color: 'inherit',
  backgroundColor: 'transparent',
  '&:hover': {
    backgroundColor: 'transparent',
    color: theme.palette.text.primary,
  },
}))

interface BackButtonProps {
  label?: string
  fallbackHref?: string
  size?: ButtonProps['size']
}

export default function BackButton({
  label = 'Voltar',
  fallbackHref = '/',
  size = 'small',
}: BackButtonProps) {
  const navigate = useNavigate()

  return (
    <BackButtonRoot
      startIcon={<ArrowBackIcon />}
      onClick={() => {
        if (window.history.length > 1) {
          navigate(-1)
        } else {
          navigate(fallbackHref)
        }
      }}
      size={size}
      variant="text"
    >
      {label}
    </BackButtonRoot>
  )
}
