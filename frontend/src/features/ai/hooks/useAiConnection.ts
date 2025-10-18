import { useEffect } from 'react';
import { useAiStore } from '../../../store/ai';

export const useAiConnection = () => {
  const resendPending = useAiStore((state) => state.resendPending);

  useEffect(() => {
    const handleOnline = () => {
      resendPending();
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [resendPending]);
};
