import { apiClient } from './client';
import type {
  AdapterDescriptor,
  ErrorReview,
  KernelExtendedStatus,
  KernelRootStatus,
  KernelRouteRequest,
  KernelRouteResponse,
  PagedResponse,
  ResolverResponse,
  TrustEvent,
  TrustMap,
  TrustTimelineResponse,
} from '../types/api';

export async function getRootStatus() {
  const { data } = await apiClient.get<KernelRootStatus>('/');
  return data;
}

export async function getKernelStatus() {
  const { data } = await apiClient.get<KernelExtendedStatus>('/kernel/status');
  return data;
}

export async function getTrustScores() {
  const { data } = await apiClient.get<TrustMap>('/trust');
  return data;
}

export async function getTrustEvents(limit = 25, offset = 0) {
  const { data } = await apiClient.get<PagedResponse<TrustEvent>>('/trust/events', {
    params: { limit, offset },
  });
  return data;
}

export async function getTrustTimeline(agent: string) {
  const { data } = await apiClient.get<TrustTimelineResponse>('/trust/timeline', {
    params: { agent },
  });
  return data;
}

export async function resolveEntity(entity: string) {
  const { data } = await apiClient.get<ResolverResponse>(`/resolve/${encodeURIComponent(entity)}`);
  return data;
}

export async function routeKernelMessage(payload: KernelRouteRequest) {
  const { data } = await apiClient.post<KernelRouteResponse>('/kernel/route', payload, {
    headers: {
      'X-Intent': 'WRITE',
    },
  });
  return data;
}

export async function getErrorReviews(limit = 25, offset = 0) {
  const { data } = await apiClient.get<PagedResponse<ErrorReview>>('/audit/error-reviews', {
    params: { limit, offset },
  });
  return data;
}

export async function getAdapters() {
  const { data } = await apiClient.get<AdapterDescriptor[]>('/kernel/adapters');
  return data;
}
