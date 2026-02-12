import type { TrustRow } from '../types/api';

export function TrustBarChart({ rows }: { rows: TrustRow[] }) {
  const maxTrust = Math.max(...rows.map((r) => r.trust), 1);

  return (
    <div className="chart">
      {rows.map((row) => (
        <div key={row.agent} className="bar-row">
          <span>{row.agent}</span>
          <div className="bar-wrap">
            <div className="bar" style={{ width: `${(row.trust / maxTrust) * 100}%` }} />
          </div>
          <strong>{row.trust.toFixed(2)}</strong>
        </div>
      ))}
    </div>
  );
}
