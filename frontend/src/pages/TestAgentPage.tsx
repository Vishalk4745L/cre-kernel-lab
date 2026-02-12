import { type FormEvent, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { routeKernelMessage } from '../api/kernelApi';
import type { KernelRouteResponse } from '../types/api';

export function TestAgentPage() {
  const [adapterId, setAdapterId] = useState('mock-agent');
  const [content, setContent] = useState('Hello from CRE UI control panel');
  const [response, setResponse] = useState<KernelRouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      setError(null);
      const data = await routeKernelMessage({ adapter_id: adapterId, content });
      setResponse(data);
    } catch (err) {
      setResponse(null);
      setError((err as Error).message);
    }
  }

  return (
    <section>
      <PageHeader
        title="Test Agent View"
        description="Simulate kernel-to-adapter routing and inspect adapter response quality and ownership."
      />
      <form className="panel" onSubmit={onSubmit}>
        <label htmlFor="adapterId">Adapter ID</label>
        <input id="adapterId" value={adapterId} onChange={(e) => setAdapterId(e.target.value)} />

        <label htmlFor="content">Message</label>
        <textarea id="content" rows={4} value={content} onChange={(e) => setContent(e.target.value)} />

        <button type="submit">Run Kernel Route</button>
      </form>

      {error && <p className="error">{error}</p>}

      {response && (
        <div className="panel">
          <h3>Adapter Response</h3>
          <p>
            <strong>Adapter:</strong> {response.agent}
          </p>
          <p>
            <strong>Reply:</strong> {response.reply}
          </p>
          <p>
            <strong>Confidence:</strong> {response.confidence.toFixed(3)}
          </p>
          <p>
            <strong>Status:</strong> {response.status}
          </p>
        </div>
      )}
    </section>
  );
}
