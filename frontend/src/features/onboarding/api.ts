import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import type {
  LifestyleCreate,
  LifestyleResponse,
  MedicalHistoryCreate,
  MedicalHistoryResponse,
} from '@/types/api'

// --- GET hooks (for checking existence on dashboard) ---

export function useGetLifestyle(enabled = true) {
  return useQuery({
    queryKey: qk.lifestyle,
    queryFn: async () => {
      const { data } = await api.get<LifestyleResponse>('/api/v1/lifestyle/')
      return data
    },
    enabled,
    retry: false,
  })
}

export function useGetMedicalHistory(enabled = true) {
  return useQuery({
    queryKey: qk.medicalHistory,
    queryFn: async () => {
      const { data } = await api.get<MedicalHistoryResponse>('/api/v1/medical-history/')
      return data
    },
    enabled,
    retry: false,
  })
}

// --- POST hooks (for onboarding creation) ---

export function useCreateLifestyle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: LifestyleCreate) => {
      const { data } = await api.post<LifestyleResponse>('/api/v1/lifestyle/', body)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.lifestyle }),
  })
}

export function useCreateMedicalHistory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: MedicalHistoryCreate) => {
      const { data } = await api.post<MedicalHistoryResponse>('/api/v1/medical-history/', body)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.medicalHistory }),
  })
}
export function useUpdateLifestyle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: Partial<LifestyleCreate>) => {
      const { data } = await api.patch<LifestyleResponse>('/api/v1/lifestyle/', body)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.lifestyle }),
  })
}

export function useUpdateMedicalHistory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: Partial<MedicalHistoryCreate>) => {
      const { data } = await api.patch<MedicalHistoryResponse>('/api/v1/medical-history/', body)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.medicalHistory }),
  })
}

// --- DELETE hooks ---

export function useDeleteLifestyle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/lifestyle/')
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.lifestyle }),
  })
}

export function useDeleteMedicalHistory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/medical-history/')
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.medicalHistory }),
  })
}
