import { z, type ZodTypeAny } from 'zod'
import type { CategoryFieldResponse } from '~/types'

export function buildFieldSchema(fields: CategoryFieldResponse[]) {
  const shape: Record<string, ZodTypeAny> = {}

  for (const field of fields) {
    let schema: ZodTypeAny

    switch (field.field_type) {
      case 'number':
        schema = z.coerce.number()
        break
      case 'date':
        schema = z.string()
        break
      case 'select':
        schema = z.string()
        break
      case 'file':
        schema = z.any()
        break
      case 'text':
      case 'textarea':
      default:
        schema = z.string()
        break
    }

    if (!field.is_required) {
      schema = schema.optional()
    }

    shape[field.name] = schema
  }

  return z.object(shape)
}
