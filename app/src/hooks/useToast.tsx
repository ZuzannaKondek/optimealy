import { useState, useCallback } from 'react';
import { Toast, ToastType } from '../components/common/Toast';

interface ToastConfig {
  message: string;
  type: ToastType;
}

export const useToast = () => {
  const [toastConfig, setToastConfig] = useState<ToastConfig | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    setToastConfig({ message, type });
    setIsVisible(true);
  }, []);

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
    ToastContainer,
  };
};
