import { useCallback, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { deleteAdapter, getAdapters, registerAdapter } from '../api/kernelApi';
import type { AdapterDescriptor } from '../types/api';
import { usePolling } from '../hooks/usePolling';
import { useToast } from '../components/ToastProvider';

export function AdapterRegistryPage() {
  const [adapters, setAdapters] = useState<AdapterDescriptor[]>([]);
  const [adapterId, setAdapterId] = useState('');
  const [adapterType, setAdapterType] = useState('agent');
  const { pushError } = useToast();

  const load = useCallback(async () => {
    try {
      const adapterList = await getAdapters();
      setAdapters(Array.isArray(adapterList) ? adapterList : []);
    } catch {
      setAdapters([]);
    }
  }, []);

  usePolling(load, 10000);

  const onRegister = async () => {
    try {
      await registerAdapter(adapterId, adapterType);
      setAdapterId('');
      await load();
    } catch {
      pushError('Failed to register adapter');
    }
  };

  const onDelete = async (id: string) => {
    try {
      await deleteAdapter(id);
      await load();
    } catch {
      pushError('Failed to delete adapter');
    }
  };

  return (
    <section>
      <PageHeader
        title="Adapter Registry View"
        description="Registered adapter list, health snapshot, and lifecycle controls."
      />

      <div className="panel card inline-form">
        <input placeholder="adapter-id" value={adapterId} onChange={(e) => setAdapterId(e.target.value)} />
        <input placeholder="adapter-type" value={adapterType} onChange={(e) => setAdapterType(e.target.value)} />
        <button onClick={onRegister} disabled={!adapterId.trim()}>
          Register
        </button>
      </div>

      <div className="panel card">
        {adapters.length === 0 ? (
          <p>No adapters registered.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Adapter ID</th>
                <th>Type</th>
                <th>Health</th>
                <th>Capabilities</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {adapters.map((adapter) => (
                <tr key={adapter.adapter_id}>
                  <td>{adapter.adapter_id}</td>
                  <td>{adapter.adapter_type}</td>
                  <td>{JSON.stringify(adapter.health)}</td>
                  <td>{JSON.stringify(adapter.capabilities)}</td>
                  <td>
                    {adapter.adapter_id !== 'mock-agent' && <button onClick={() => onDelete(adapter.adapter_id)}>Delete</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
