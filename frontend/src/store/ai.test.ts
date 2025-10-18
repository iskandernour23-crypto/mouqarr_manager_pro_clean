import { beforeEach, describe, expect, it } from 'vitest';
import { useAiStore } from './ai';

const resetStore = () => {
  useAiStore.setState({
    messages: [],
    suggestions: [],
    quickPrompts: useAiStore.getState().quickPrompts,
    settings: useAiStore.getState().settings,
    streaming: false,
    error: undefined,
    pendingQueue: [],
  });
};

describe('AI store', () => {
  beforeEach(() => {
    resetStore();
  });

  it('queues offline messages', async () => {
    Object.defineProperty(globalThis, 'navigator', {
      value: { onLine: false },
      configurable: true,
    });
    await useAiStore.getState().sendMessage('مرحبا');
    expect(useAiStore.getState().messages[0].pending).toBe(true);
    expect(useAiStore.getState().pendingQueue).toHaveLength(1);
  });

  it('updates settings', () => {
    useAiStore.getState().updateSettings({ language: 'en' });
    expect(useAiStore.getState().settings.language).toBe('en');
  });
});
