import { useEffect } from 'react';

export type TrustStreamEvent = {
  agent: string;
  trust: number;
  change: number;
  reason: string;
  timestamp: number;
};

export function useTrustStream(onEvent: (evt: TrustStreamEvent) => void) {
  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
    const wsUrl = base.replace('http', 'ws') + '/ws/trust';
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (msg) => {
      try {
        onEvent(JSON.parse(msg.data));
      } catch {
        // ignore
      }
    };

    ws.onopen = () => {
      ws.send('subscribe');
    };

    return () => ws.close();
  }, [onEvent]);
}
