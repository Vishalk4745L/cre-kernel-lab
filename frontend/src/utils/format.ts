export function formatTimestamp(ts?: number | null) {
  if (!ts) return '—';
  return new Date(ts * 1000).toLocaleString();
}

export function toPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
