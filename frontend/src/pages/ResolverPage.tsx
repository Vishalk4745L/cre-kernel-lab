import { useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { resolveEntity } from '../api/kernelApi';
import type { ResolverResponse } from '../types/api';
import { formatTimestamp } from '../utils/format';

export function ResolverPage() {
  const [entity, setEntity] = useState('');
  const [result, setResult] = useState<ResolverResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onResolve() {
    try {
      setError(null);
      const data = await resolveEntity(entity);
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
      setResult(null);
    }
  }

  return (
    <section>
      <PageHeader
        title="Resolver View"
        description="Resolve canonical entity values and inspect confidence, reason, and timing signals."
      />
      <div className="panel">
        <label htmlFor="entity">Entity</label>
        <div className="inline-form">
          <input
            id="entity"
            value={entity}
            placeholder="e.g., moon_landing_1969"
            onChange={(e) => setEntity(e.target.value)}
          />
          <button onClick={onResolve} disabled={!entity.trim()}>
            Resolve
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>
      {result && (
        <div className="panel">
          <h3>Resolution Result</h3>
          <p>
            <strong>Value:</strong> {result.value ?? 'null'}
          </p>
          <p>
            <strong>Confidence:</strong> {result.confidence.toFixed(3)}
          </p>
          <p>
            <strong>Reason:</strong> {result.reason}
          </p>
          <p>
            <strong>Timestamp:</strong> {formatTimestamp(result.timestamp)}
          </p>
        </div>
      )}
    </section>
  );
}
