import {
    Box,
    Button,
    Divider,
    Drawer,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    TextField,
    Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'

export interface FieldConfig {
  name: string
  label: string
  type: 'text' | 'number' | 'select'
  required?: boolean
  options?: Array<{ value: any; label: string }>
  disabled?: boolean
}

interface CrudFormProps {
  open: boolean
  onClose: () => void
  onSave: (data: any) => Promise<void>
  title: string
  fields: FieldConfig[]
  initialData?: any
  isEdit?: boolean
}

export default function CrudForm({
  open,
  onClose,
  onSave,
  title,
  fields,
  initialData,
  isEdit = false,
}: CrudFormProps) {
  const [formData, setFormData] = useState<any>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (open) {
      if (initialData) {
        setFormData(initialData)
      } else {
        // Initialize with empty values
        const emptyData: any = {}
        fields.forEach((field) => {
          emptyData[field.name] = field.type === 'number' ? 0 : ''
        })
        setFormData(emptyData)
      }
    }
  }, [open, initialData, fields])

  const handleChange = (name: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      await onSave(formData)
      onClose()
    } catch (error) {
      console.error('Erro ao salvar:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: { xs: '100vw', sm: 500 }, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">{title}</Typography>
        </Box>

        <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
          {fields.map((field) => {
            if (field.type === 'select') {
              return (
                <FormControl key={field.name} fullWidth margin="normal" required={field.required}>
                  <InputLabel>{field.label}</InputLabel>
                  <Select
                    value={formData[field.name] || ''}
                    label={field.label}
                    onChange={(e) => handleChange(field.name, e.target.value)}
                    disabled={field.disabled}
                  >
                    {field.options?.map((opt) => (
                      <MenuItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )
            }

            return (
              <TextField
                key={field.name}
                label={field.label}
                type={field.type}
                value={formData[field.name] || ''}
                onChange={(e) =>
                  handleChange(
                    field.name,
                    field.type === 'number' ? Number(e.target.value) : e.target.value
                  )
                }
                fullWidth
                margin="normal"
                required={field.required}
                disabled={field.disabled}
              />
            )
          })}
        </Box>

        {/* Footer Actions */}
        <Divider />
        <Box sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} variant="contained" disabled={loading}>
              {loading ? 'Salvando...' : isEdit ? 'Atualizar' : 'Criar'}
            </Button>
          </Stack>
        </Box>
      </Box>
    </Drawer>
  )
}
