import { Outlet } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';

export function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
