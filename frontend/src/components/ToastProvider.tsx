import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

type Toast = { id: number; message: string };

type ToastContextType = {
  pushError: (message: string) => void;
};

const ToastContext = createContext<ToastContextType>({ pushError: () => undefined });

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const value = useMemo(
    () => ({
      pushError: (message: string) => {
        const id = Date.now();
        setToasts((prev) => [...prev, { id, message }]);
        window.setTimeout(() => {
          setToasts((prev) => prev.filter((x) => x.id !== id));
        }, 3500);
      },
    }),
    []
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-stack">
        {toasts.map((toast) => (
          <div key={toast.id} className="toast toast-error">
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
