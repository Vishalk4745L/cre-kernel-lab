import { createBrowserRouter } from 'react-router-dom';
import { App } from '../App';
import { DashboardPage } from '../pages/DashboardPage';
import { TrustPage } from '../pages/TrustPage';
import { ResolverPage } from '../pages/ResolverPage';
import { TestAgentPage } from '../pages/TestAgentPage';
import { AuditPage } from '../pages/AuditPage';
import { AdapterRegistryPage } from '../pages/AdapterRegistryPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'trust', element: <TrustPage /> },
      { path: 'resolver', element: <ResolverPage /> },
      { path: 'test-agent', element: <TestAgentPage /> },
      { path: 'audit', element: <AuditPage /> },
      { path: 'adapters', element: <AdapterRegistryPage /> },
    ],
  },
]);
