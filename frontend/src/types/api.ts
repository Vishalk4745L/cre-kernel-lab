export type KernelRootStatus = {
  status: string;
};

export type KernelExtendedStatus = {
  status: string;
  version: string;
  adapters_registered: number;
  adapters: string[];
  timestamp: number;
};

export type TrustMap = Record<string, number>;

export type TrustRow = {
  agent: string;
  trust: number;
};

export type TrustEvent = {
  agent: string;
  change: number;
  reason: string;
  timestamp: number;
};

export type TrustTimelinePoint = {
  timestamp: number;
  trust: number;
};

export type TrustTimelineResponse = {
  agent: string;
  timeline: TrustTimelinePoint[];
};

export type ResolverResponse = {
  entity: string;
  value: string | null;
  confidence: number;
  reason: string;
  timestamp: number;
  status?: string;
};

export type KernelRouteRequest = {
  adapter_id: string;
  content: string;
};

export type KernelRouteResponse = {
  agent: string;
  reply: string;
  confidence: number;
  status: string;
};

export type ErrorReview = {
  id: number;
  reviewer_agent: string;
  target_agent: string;
  entity: string;
  observed_value: string | null;
  expected_value: string | null;
  error_type: string;
  confidence: number;
  evidence: string | null;
  timestamp: number;
};

export type PagedResponse<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type AdapterDescriptor = {
  adapter_id: string;
  adapter_type: string;
  capabilities: Record<string, unknown>;
  health: Record<string, unknown>;
};
