import { Outlet } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { useEffect, useState } from 'react';

export function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>(() =>
    (localStorage.getItem('kernel-theme') as 'dark' | 'light') || 'dark'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('kernel-theme', theme);
  }, [theme]);

  return (
    <div className="app-shell">
      <Sidebar theme={theme} onToggleTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')} />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
