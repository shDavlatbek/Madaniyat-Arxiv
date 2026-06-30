import type {
  AppealTypeResponse,
  ReceptionPlaceResponse,
  RegionResponse,
  RegionType,
  RetentionPeriodResponse,
} from '~/types'

export interface LocationRegion {
  id: number
  soato_id: number
  name_uz: string
  name_oz: string
  name_ru: string
}

export interface LocationDistrict {
  id: number
  region_id: number
  soato_id: number
  name_uz: string
  name_oz: string
  name_ru: string
}

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

  async function listLocationRegions() {
    return apiFetch<LocationRegion[]>('/api/locations/regions')
  }

  async function listLocationDistricts() {
    return apiFetch<LocationDistrict[]>('/api/locations/districts')
  }

  return {
    listRegions,
    listReceptionPlaces,
    listAppealTypes,
    listRetentionPeriods,
    listLocationRegions,
    listLocationDistricts,
  }
}

