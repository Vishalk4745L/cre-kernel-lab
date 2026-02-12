import { useCallback, useMemo, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { TrustBarChart } from '../components/TrustBarChart';
import { getTrustScores, getTrustTimeline } from '../api/kernelApi';
import type { TrustRow, TrustTimelinePoint } from '../types/api';
import { usePolling } from '../hooks/usePolling';
import { formatTimestamp } from '../utils/format';

export function TrustPage() {
  const [rows, setRows] = useState<TrustRow[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [timeline, setTimeline] = useState<TrustTimelinePoint[]>([]);

  const loadScores = useCallback(async () => {
    const trustMap = await getTrustScores();
    const nextRows = Object.entries(trustMap)
      .map(([agent, trust]) => ({ agent, trust }))
      .sort((a, b) => b.trust - a.trust);
    setRows(nextRows);
    if (!selectedAgent && nextRows.length > 0) {
      setSelectedAgent(nextRows[0].agent);
    }
  }, [selectedAgent]);

  const loadTimeline = useCallback(async () => {
    if (!selectedAgent) return;
    const data = await getTrustTimeline(selectedAgent);
    setTimeline(data.timeline);
  }, [selectedAgent]);

  usePolling(loadScores, 8000);
  usePolling(loadTimeline, 12000);

  const latestTimeline = useMemo(() => timeline.slice(-10).reverse(), [timeline]);

  return (
    <section>
      <PageHeader
        title="Trust View"
        description="Trust-scoring visibility by agent with a chart and timeline snapshots for live monitoring."
      />
      <div className="panel">
        <h3>Trust Score Table</h3>
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Trust</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.agent}>
                <td>{row.agent}</td>
                <td>{row.trust.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="panel">
        <h3>Trust Graph (Bar)</h3>
        <TrustBarChart rows={rows} />
      </div>
      <div className="panel">
        <h3>Timeline for Selected Agent</h3>
        <select value={selectedAgent} onChange={(e) => setSelectedAgent(e.target.value)}>
          {rows.map((row) => (
            <option key={row.agent} value={row.agent}>
              {row.agent}
            </option>
          ))}
        </select>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Trust</th>
            </tr>
          </thead>
          <tbody>
            {latestTimeline.map((point) => (
              <tr key={`${point.timestamp}-${point.trust}`}>
                <td>{formatTimestamp(point.timestamp)}</td>
                <td>{point.trust.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
