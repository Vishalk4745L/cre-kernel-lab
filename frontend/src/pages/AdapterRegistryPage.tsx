import { useCallback, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { getAdapters } from '../api/kernelApi';
import type { AdapterDescriptor } from '../types/api';
import { usePolling } from '../hooks/usePolling';

export function AdapterRegistryPage() {
  const [adapters, setAdapters] = useState<AdapterDescriptor[]>([]);

  const load = useCallback(async () => {
    const data = await getAdapters();
    setAdapters(data);
  }, []);

  usePolling(load, 10000);

  return (
    <section>
      <PageHeader
        title="Adapter Registry View"
        description="Registered adapter list, health snapshot, and capability metadata for future multi-protocol scaling."
      />
      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Adapter ID</th>
              <th>Type</th>
              <th>Health</th>
              <th>Capabilities</th>
            </tr>
          </thead>
          <tbody>
            {adapters.map((adapter) => (
              <tr key={adapter.adapter_id}>
                <td>{adapter.adapter_id}</td>
                <td>{adapter.adapter_type}</td>
                <td>{JSON.stringify(adapter.health)}</td>
                <td>{JSON.stringify(adapter.capabilities)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
