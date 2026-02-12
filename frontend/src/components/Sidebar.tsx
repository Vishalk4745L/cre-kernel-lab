import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/trust', label: 'Trust View' },
  { to: '/resolver', label: 'Resolver View' },
  { to: '/test-agent', label: 'Test Agent' },
  { to: '/audit', label: 'Audit Viewer' },
  { to: '/adapters', label: 'Adapter Registry' },
];

export function Sidebar({ theme, onToggleTheme }: { theme: 'dark' | 'light'; onToggleTheme: () => void }) {
  return (
    <aside className="sidebar card">
      <h1>CRE Kernel</h1>
      <p className="subtitle">Reasoning Control Panel</p>
      <button className="theme-toggle" onClick={onToggleTheme}>
        {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
      </button>
      <nav>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
