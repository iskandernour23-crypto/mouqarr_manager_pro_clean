export interface ChatMessagePayload {
  id?: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  tool_calls?: Array<{
    id?: string;
    name: string;
    arguments: Record<string, unknown>;
  }>;
}

export interface ChatRequestPayload {
  messages: ChatMessagePayload[];
  options?: {
    model?: string;
    temperature?: number;
    lang?: string;
  };
}

export interface ChatStreamChunk {
  type: 'message' | 'tool_call' | 'tool_result' | 'error' | 'done';
  delta?: string;
  tool_name?: string;
  tool_arguments?: Record<string, unknown>;
  tool_result?: Record<string, unknown>;
  message_id?: string;
}

interface StreamCallbacks {
  onChunk?: (chunk: ChatStreamChunk) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
}

const decoder = new TextDecoder('utf-8');

const buildHeaders = () => ({
  'Content-Type': 'application/json',
  Accept: 'text/event-stream',
});

const parseSse = (buffer: string, emit: (chunk: ChatStreamChunk) => void) => {
  const events = buffer.split('\n\n');
  for (let i = 0; i < events.length - 1; i += 1) {
    const event = events[i];
    const dataLine = event
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.replace(/^data:\s*/, ''))
      .join('');
    if (!dataLine) continue;
    try {
      const parsed = JSON.parse(dataLine) as ChatStreamChunk;
      emit(parsed);
    } catch (error) {
      emit({ type: 'error', delta: 'حدث خطأ في تحليل الاستجابة.' });
    }
  }
  return events[events.length - 1];
};

export const streamChat = async (
  payload: ChatRequestPayload,
  callbacks: StreamCallbacks = {}
): Promise<void> => {
  const response = await fetch('/ai/chat', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    const error = new Error(message || 'فشل الاتصال بالمساعد.');
    callbacks.onError?.(error);
    throw error;
  }

  if (!response.body) {
    const json = await response.json();
    callbacks.onChunk?.({ type: 'message', delta: json.message?.content ?? '' });
    callbacks.onDone?.();
    return;
  }

  const reader = response.body.getReader();
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      buffer = parseSse(buffer, (chunk) => callbacks.onChunk?.(chunk));
    }
  } catch (error) {
    const err = error instanceof Error ? error : new Error('فشل في قراءة الاستجابة.');
    callbacks.onError?.(err);
  } finally {
    callbacks.onDone?.();
  }
};

export const executeAction = async (name: string, params: Record<string, unknown>) => {
  const response = await fetch('/ai/actions/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, params }),
  });
  if (!response.ok) {
    throw new Error('تعذر تنفيذ الإجراء.');
  }
  return response.json();
};

export interface SuggestionPayload {
  title: string;
  body: string;
  action?: string;
}

export const fetchSuggestions = async (): Promise<SuggestionPayload[]> => {
  const response = await fetch('/ai/suggest');
  if (!response.ok) {
    throw new Error('تعذر تحميل الاقتراحات.');
  }
  return response.json();
};
