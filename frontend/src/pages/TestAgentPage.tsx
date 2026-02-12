import { useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { runKernelRoute } from '../api/kernelApi';

export function TestAgentPage() {
  const [adapterId, setAdapterId] = useState('mock-agent');
  const [message, setMessage] = useState('Hello from CRE UI control panel');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runKernelRoute(adapterId, message);
      setResult(data);
    } catch (err) {
      console.error('Kernel route failed:', err);
      setError('Kernel route failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <PageHeader
        title="Test Agent View"
        description="Simulate kernel-to-adapter routing and inspect adapter response quality and ownership."
      />

      <div className="panel">
        <div className="inline-form">
          <label>Adapter ID</label>
          <input
            value={adapterId}
            onChange={(e) => setAdapterId(e.target.value)}
          />

          <label>Message</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <button onClick={handleRun} disabled={loading}>
            {loading ? 'Running...' : 'Run Kernel Route'}
          </button>
        </div>
      </div>

      <div className="panel">
        <h3>Result</h3>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        {!result ? (
          <p>No result yet.</p>
        ) : (
          <table>
            <tbody>
              <tr>
                <td><strong>Agent</strong></td>
                <td>{result.agent ?? adapterId}</td>
              </tr>
              <tr>
                <td><strong>Reply</strong></td>
                <td>{result.reply ?? result.content ?? 'N/A'}</td>
              </tr>
              <tr>
                <td><strong>Confidence</strong></td>
                <td>
                  {result.confidence !== undefined
                    ? Number(result.confidence).toFixed(3)
                    : '0.000'}
                </td>
              </tr>
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}