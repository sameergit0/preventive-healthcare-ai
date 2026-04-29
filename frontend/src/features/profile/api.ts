import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { qk } from '@/lib/queryKeys'
import type { Profile, ProfileGetResponse, ProfilePhotoResponse } from '@/types/api'

export function useProfile() {
  return useQuery({
    queryKey: qk.profile,
    queryFn: async () => {
      const { data } = await api.get<ProfileGetResponse>('/api/v1/profile/')
      return data
    },
  })
}

export function useCreateProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (fd: FormData) => {
      const { data } = await api.post<Profile>('/api/v1/profile/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.profile }),
  })
}

export function useUpdateProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: Partial<Omit<Profile, 'id' | 'profile_image'>>) => {
      const { data } = await api.patch<Profile>('/api/v1/profile/', body)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.profile }),
  })
}

export function useDeleteProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/profile/')
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.profile }),
  })
}

export function useUpdatePhoto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await api.put<ProfilePhotoResponse>('/api/v1/profile/photo', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.profile }),
  })
}

export function useDeletePhoto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/profile/photo')
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.profile }),
  })
}
