import type {
  AppealTypeResponse,
  ReceptionPlaceResponse,
  RegionResponse,
  RegionType,
  RetentionPeriodResponse,
} from '~/types'

/**
 * Read-only access to the seed reference tables:
 *   - Murojaat form: regions (Hudud), reception places (Qabul qilingan joy),
 *     appeal types (Murojaat turi)
 *   - Yig'ma jild form: retention periods (Saqlash muddati)
 */
export const useReferences = () => {
  const { apiFetch } = useApi()

  async function listRegions(type?: RegionType) {
    const query = type ? `?type=${type}` : ''
    return apiFetch<{ items: RegionResponse[] }>(`/api/regions${query}`)
  }

  async function listReceptionPlaces() {
    return apiFetch<{ items: ReceptionPlaceResponse[] }>('/api/reception-places')
  }

  async function listAppealTypes() {
    return apiFetch<{ items: AppealTypeResponse[] }>('/api/appeal-types')
  }

  async function listRetentionPeriods() {
    return apiFetch<{ items: RetentionPeriodResponse[] }>('/api/retention-periods')
  }

  return { listRegions, listReceptionPlaces, listAppealTypes, listRetentionPeriods }
}
