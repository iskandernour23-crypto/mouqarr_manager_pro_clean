import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { streamChat, executeAction, fetchSuggestions, type ChatRequestPayload, type ChatStreamChunk, type SuggestionPayload } from '../features/ai/api';

export type AiRole = 'user' | 'assistant' | 'tool' | 'system';

export interface AiToolCall {
  id?: string;
  name: string;
  arguments: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface AiAttachment {
  id: string;
  label: string;
  body: string;
}

export interface AiMessage {
  id: string;
  role: AiRole;
  content: string;
  createdAt: string;
  pending?: boolean;
  streaming?: boolean;
  toolCalls?: AiToolCall[];
  attachments?: AiAttachment[];
}

export interface AiSettings {
  model: string;
  temperature: number;
  language: 'ar' | 'en';
  enableTts: boolean;
}

interface AiState {
  messages: AiMessage[];
  suggestions: SuggestionPayload[];
  quickPrompts: string[];
  settings: AiSettings;
  streaming: boolean;
  error?: string;
  pendingQueue: AiMessage[];
  currentAssistantId?: string;
  sendMessage: (content: string) => Promise<void>;
  enqueueMessage: (message: AiMessage) => void;
  updateSettings: (changes: Partial<AiSettings>) => void;
  applyToolResult: (toolChunk: ChatStreamChunk) => void;
  executeQuickPrompt: (prompt: string) => Promise<void>;
  loadSuggestions: () => Promise<void>;
  resendPending: () => Promise<void>;
  cancelStream: () => void;
  runAction: (name: string, params: Record<string, unknown>) => Promise<void>;
}

const QUICK_PROMPTS = [
  'من المتأخر هذا الشهر؟',
  'أنشئ فاتورة لشقة 12 عن شهر نوفمبر',
  'كم إجمالي المدفوعات هذا الأسبوع؟',
  'أضف مقيمًا جديدًا باسم أحمد علي',
  'موعد صيانة مطفأة حريق المبنى A؟',
];

const createId = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

const baseSettings: AiSettings = {
  model: 'gpt-4o-mini',
  temperature: 0.2,
  language: 'ar',
  enableTts: false,
};

interface StreamController {
  abort: () => void;
}

export const useAiStore = create<AiState>()(devtools((set, get) => {
  let controller: StreamController | undefined;

  const appendMessage = (message: AiMessage) => {
    set((state) => ({ messages: [...state.messages, message] }));
  };

  const updateAssistantMessage = (id: string, delta: string) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content: msg.content + delta } : msg
      ),
    }));
  };

  const setStreaming = (value: boolean) => {
    set({ streaming: value });
  };

  const handleStreamChunk = (assistantId: string, chunk: ChatStreamChunk) => {
    if (chunk.type === 'message' && chunk.delta) {
      updateAssistantMessage(assistantId, chunk.delta);
    }
    if (chunk.type === 'tool_result' && chunk.tool_result) {
      const message: AiMessage = {
        id: chunk.message_id ?? createId(),
        role: 'tool',
        content: JSON.stringify(chunk.tool_result, null, 2),
        createdAt: new Date().toISOString(),
      };
      appendMessage(message);
    }
    if (chunk.type === 'error' && chunk.delta) {
      set({ error: chunk.delta });
    }
  };

  const finalizeAssistant = (assistantId: string) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === assistantId ? { ...msg, streaming: false } : msg
      ),
    }));
  };

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    const userMessage: AiMessage = {
      id: createId(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
      pending: !navigator.onLine,
    };
    appendMessage(userMessage);

    if (!navigator.onLine) {
      set((state) => ({ pendingQueue: [...state.pendingQueue, userMessage] }));
      return;
    }

    set({ error: undefined });
    const assistantId = createId();
    appendMessage({
      id: assistantId,
      role: 'assistant',
      content: '',
      createdAt: new Date().toISOString(),
      streaming: true,
    });
    setStreaming(true);

    const history = get()
      .messages
      .filter((msg) => msg.id !== assistantId)
      .map((msg) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        tool_calls: msg.toolCalls?.map((tool) => ({
          id: tool.id,
          name: tool.name,
          arguments: tool.arguments,
        })),
      }));

    const payload: ChatRequestPayload = {
      messages: history,
      options: {
        lang: get().settings.language,
        model: get().settings.model,
        temperature: get().settings.temperature,
      },
    };

    controller = {
      abort: () => {
        setStreaming(false);
      },
    };

    try {
      await streamChat(payload, {
        onChunk: (chunk) => handleStreamChunk(assistantId, chunk),
        onDone: () => finalizeAssistant(assistantId),
        onError: (err) => set({ error: err.message }),
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : String(error),
      });
    } finally {
      finalizeAssistant(assistantId);
      setStreaming(false);
      controller = undefined;
    }
  };

  const runAction = async (name: string, params: Record<string, unknown>) => {
    try {
      const result = await executeAction(name, params);
      const message: AiMessage = {
        id: createId(),
        role: 'tool',
        content: JSON.stringify(result, null, 2),
        createdAt: new Date().toISOString(),
      };
      appendMessage(message);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : String(error) });
    }
  };

  return {
    messages: [],
    suggestions: [],
    quickPrompts: QUICK_PROMPTS,
    settings: baseSettings,
    streaming: false,
    pendingQueue: [],
    sendMessage,
    enqueueMessage: appendMessage,
    updateSettings: (changes) =>
      set((state) => ({ settings: { ...state.settings, ...changes } })),
    applyToolResult: (chunk) => {
      if (chunk.tool_result) {
        const message: AiMessage = {
          id: chunk.message_id ?? createId(),
          role: 'tool',
          content: JSON.stringify(chunk.tool_result, null, 2),
          createdAt: new Date().toISOString(),
        };
        appendMessage(message);
      }
    },
    executeQuickPrompt: (prompt: string) => sendMessage(prompt),
    loadSuggestions: async () => {
      try {
        const suggestions = await fetchSuggestions();
        set({ suggestions });
      } catch (error) {
        set({ error: error instanceof Error ? error.message : String(error) });
      }
    },
    resendPending: async () => {
      const queue = get().pendingQueue;
      if (!queue.length || !navigator.onLine) return;
      set({ pendingQueue: [] });
      for (const message of queue) {
        await sendMessage(message.content);
      }
    },
    cancelStream: () => {
      controller?.abort();
      setStreaming(false);
    },
    runAction,
  };
}));
