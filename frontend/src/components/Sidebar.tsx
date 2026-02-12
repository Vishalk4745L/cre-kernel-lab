import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/trust', label: 'Trust View' },
  { to: '/resolver', label: 'Resolver View' },
  { to: '/test-agent', label: 'Test Agent' },
  { to: '/audit', label: 'Audit Viewer' },
  { to: '/adapters', label: 'Adapter Registry' },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <h1>CRE Kernel</h1>
      <p className="subtitle">Reasoning Control Panel</p>
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
