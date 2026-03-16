import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { Toast, ToastType } from '../components/common/Toast';

interface ToastConfig {
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
  showSaved: (item?: string) => void;
  showStarted: (name: string) => void;
  showDeleted: (item?: string) => void;
  showUpdated: (item?: string) => void;
  showAdded: (item?: string) => void;
  showConfirmed: (action?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useGlobalToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useGlobalToast must be used within ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toastConfig, setToastConfig] = useState<ToastConfig | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    setToastConfig({ message, type });
    setIsVisible(true);
  }, []);

  const hideToast = useCallback(() => {
    setIsVisible(false);
  }, []);

  // Convenience methods with Polish messages
  const showSaved = useCallback((item?: string) => {
    const message = item ? `${item} zapisano pomyślnie` : 'Zapisano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showStarted = useCallback((name: string) => {
    showToast(`${name} rozpoczęta`, 'success');
  }, [showToast]);

  const showDeleted = useCallback((item?: string) => {
    const message = item ? `${item} usunięto` : 'Usunięto pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showUpdated = useCallback((item?: string) => {
    const message = item ? `${item} zaktualizowano` : 'Zaktualizowano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showAdded = useCallback((item?: string) => {
    const message = item ? `${item} dodano` : 'Dodano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showConfirmed = useCallback((action?: string) => {
    const message = action ? `${action} potwierdzone` : 'Potwierdzono';
    showToast(message, 'success');
  }, [showToast]);

  return (
    <ToastContext.Provider
      value={{ showToast, showSaved, showStarted, showDeleted, showUpdated, showAdded, showConfirmed }}
    >
      {children}
      <Toast
        message={toastConfig?.message || ''}
        type={toastConfig?.type || 'success'}
        visible={isVisible}
        onHide={hideToast}
      />
    </ToastContext.Provider>
  );
};

// Backwards compatibility - old useToast hook
export const useToast = () => {
  const [toastConfig, setToastConfig] = useState<ToastConfig | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    setToastConfig({ message, type });
    setIsVisible(true);
  }, []);

  const showSaved = useCallback((item?: string) => {
    const message = item ? `${item} zapisano pomyślnie` : 'Zapisano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showStarted = useCallback((name: string) => {
    showToast(`${name} rozpoczęta`, 'success');
  }, [showToast]);

  const showDeleted = useCallback((item?: string) => {
    const message = item ? `${item} usunięto` : 'Usunięto pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showUpdated = useCallback((item?: string) => {
    const message = item ? `${item} zaktualizowano` : 'Zaktualizowano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showAdded = useCallback((item?: string) => {
    const message = item ? `${item} dodano` : 'Dodano pomyślnie';
    showToast(message, 'success');
  }, [showToast]);

  const showConfirmed = useCallback((action?: string) => {
    const message = action ? `${action} potwierdzone` : 'Potwierdzono';
    showToast(message, 'success');
  }, [showToast]);

  const hideToast = useCallback(() => {
    setIsVisible(false);
  }, []);

  const ToastContainer = useCallback(
    () => (
      <Toast
        message={toastConfig?.message || ''}
        type={toastConfig?.type || 'success'}
        visible={isVisible}
        onHide={hideToast}
      />
    ),
    [toastConfig, isVisible, hideToast]
  );

  return {
    showToast,
    showSaved,
    showStarted,
    showDeleted,
    showUpdated,
    showAdded,
    showConfirmed,
    ToastContainer,
  };
};
