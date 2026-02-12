import { useCallback, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { getKernelStatus, getRootStatus, getTrustScores } from '../api/kernelApi';
import type { KernelExtendedStatus } from '../types/api';
import { usePolling } from '../hooks/usePolling';
import { formatTimestamp } from '../utils/format';

export function DashboardPage() {
  const [root, setRoot] = useState('loading');
  const [kernel, setKernel] = useState<KernelExtendedStatus | null>(null);
  const [agentCount, setAgentCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const [rootResp, kernelResp, trustMap] = await Promise.all([
        getRootStatus(),
        getKernelStatus(),
        getTrustScores(),
      ]);
      setRoot(rootResp.status);
      setKernel(kernelResp);
      setAgentCount(Object.keys(trustMap).length);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  usePolling(load, 15000);

  return (
    <section>
      <PageHeader
        title="Dashboard"
        description="Live kernel health, version metadata, and top-level trust-system metrics."
      />
      {error && <p className="error">{error}</p>}
      <div className="stats-grid">
        <StatCard label="Kernel Status" value={root} />
        <StatCard label="Kernel Version" value={kernel?.version ?? '—'} />
        <StatCard label="Registered Adapters" value={kernel?.adapters_registered ?? 0} />
        <StatCard label="Agents with Trust Entries" value={agentCount} />
      </div>
      <div className="panel">
        <h3>Health Indicators</h3>
        <ul>
          <li>Service heartbeat: {root}</li>
          <li>Adapter registry loaded: {kernel ? 'yes' : 'no'}</li>
          <li>Last update: {formatTimestamp(kernel?.timestamp)}</li>
        </ul>
      </div>
    </section>
  );
}
