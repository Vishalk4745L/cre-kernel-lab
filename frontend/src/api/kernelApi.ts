import { apiClient } from './client';
import type {
  AdapterDescriptor,
  ErrorReview,
  KernelExtendedStatus,
  KernelRootStatus,
  KernelRouteResponse,
  PagedResponse,
  ResolverResponse,
  TrustEvent,
  TrustMap,
} from '../types/api';

/* ===========================
   ROOT + STATUS
=========================== */

export async function getRootStatus(): Promise<KernelRootStatus> {
  const res = await apiClient.get<{ ok: boolean; data: KernelRootStatus }>('/');
  return res.data?.data ?? {};
}

export async function getKernelStatus(): Promise<KernelExtendedStatus> {
  const res = await apiClient.get<{ ok: boolean; data: KernelExtendedStatus }>(
    '/kernel/status'
  );
  return res.data?.data ?? {};
}

/* ===========================
   TRUST
=========================== */

export async function getTrustScores(): Promise<TrustMap> {
  const res = await apiClient.get<{ ok: boolean; data: TrustMap }>('/trust');
  return res.data?.data ?? {};
}

export async function getTrustEvents(limit = 25, offset = 0) {
  const res = await apiClient.get<{
    ok: boolean;
    data: PagedResponse<TrustEvent>;
  }>('/trust/events', {
    params: { limit, offset },
  });

  return res.data?.data ?? {
    items: [],
    total: 0,
    limit,
    offset,
  };
}

export async function getTrustTimeline(agent: string) {
  const res = await apiClient.get<{
    ok: boolean;
    data: { timestamp: number; trust: number }[];
  }>('/trust/timeline', {
    params: { agent },
  });

  return res.data?.data ?? [];
}

/* ===========================
   RESOLVER
=========================== */

export async function resolveEntity(entity: string): Promise<ResolverResponse> {
  const res = await apiClient.get<{ ok: boolean; data: ResolverResponse }>(
    `/resolve/${encodeURIComponent(entity)}`
  );

  return res.data?.data ?? {};
}

/* ===========================
   KERNEL ROUTE (FIXED)
=========================== */

export async function runKernelRoute(
  adapterId: string,
  message: string
): Promise<KernelRouteResponse> {
  const res = await apiClient.post<{
    ok: boolean;
    data: KernelRouteResponse;
  }>(
    '/kernel/route',
    {
      adapter_id: adapterId,
      content: message,
    },
    {
      headers: {
        'X-Intent': 'WRITE',
      },
    }
  );

  return res.data?.data ?? {};
}

/* backward alias */
export const routeKernelMessage = runKernelRoute;

/* ===========================
   AUDIT
=========================== */

export async function getErrorReviews(limit = 25, offset = 0) {
  const res = await apiClient.get<{
    ok: boolean;
    data: PagedResponse<ErrorReview>;
  }>('/audit/error-reviews', {
    params: { limit, offset },
  });

  return res.data?.data ?? {
    items: [],
    total: 0,
    limit,
    offset,
  };
}

/* ===========================
   ADAPTERS
=========================== */

export async function getAdapters(): Promise<AdapterDescriptor[]> {
  const res = await apiClient.get<{
    ok: boolean;
    data: AdapterDescriptor[];
  }>('/kernel/adapters');

  return res.data?.data ?? [];
}