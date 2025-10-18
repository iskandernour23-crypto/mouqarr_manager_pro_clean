export const flushOfflineQueue = () => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage('flush-queue');
  }
};

export const apiFetch = async <T>(input: RequestInfo, init?: RequestInit): Promise<T> => {
  if (!navigator.onLine && init && init.method && init.method !== 'GET') {
    return Promise.resolve({ status: 'queued', offline: true } as unknown as T);
  }

  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error('تعذر إكمال العملية');
  }
  return response.json();
};

window.addEventListener('online', () => flushOfflineQueue());
