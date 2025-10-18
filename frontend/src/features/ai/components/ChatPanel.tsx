import { FormEvent, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperAirplaneIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import MessageBubble from './MessageBubble';
import ActionCard from './ActionCard';
import AiSettingsDrawer from './AiSettingsDrawer';
import { useAiStore } from '../../../store/ai';
import { useAiConnection } from '../hooks/useAiConnection';

interface ChatPanelProps {
  open: boolean;
  onClose: () => void;
}

const ChatPanel = ({ open, onClose }: ChatPanelProps) => {
  const { t } = useTranslation();
  const messages = useAiStore((state) => state.messages);
  const quickPrompts = useAiStore((state) => state.quickPrompts);
  const sendMessage = useAiStore((state) => state.sendMessage);
  const streaming = useAiStore((state) => state.streaming);
  const error = useAiStore((state) => state.error);
  const loadSuggestions = useAiStore((state) => state.loadSuggestions);
  const suggestions = useAiStore((state) => state.suggestions);
  const [input, setInput] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isOffline, setIsOffline] = useState(typeof navigator !== 'undefined' ? !navigator.onLine : false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useAiConnection();

  useEffect(() => {
    const handleStatus = () => setIsOffline(!navigator.onLine);
    window.addEventListener('online', handleStatus);
    window.addEventListener('offline', handleStatus);
    return () => {
      window.removeEventListener('online', handleStatus);
      window.removeEventListener('offline', handleStatus);
    };
  }, []);

  useEffect(() => {
    if (open) {
      loadSuggestions();
    }
  }, [open, loadSuggestions]);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, streaming]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim()) return;
    await sendMessage(input.trim());
    setInput('');
  };

  if (!open) return null;

  return (
    <aside className="fixed inset-y-0 right-0 z-30 flex w-full max-w-xl bg-slate-50 dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-xl">
      <div className="flex h-full w-full flex-col">
        <header className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">مساعد المنصة الذكي</h2>
            <p className="text-xs text-slate-500 mt-1">اسألني عن الفواتير، المقيمين، الصيانة...</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSettingsOpen(true)}
              className="inline-flex items-center justify-center w-8 h-8 rounded-full border border-slate-300 text-slate-600 hover:text-primary-600"
            >
              <Cog6ToothIcon className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="text-xs text-slate-500 hover:text-primary-600"
            >
              إغلاق
            </button>
          </div>
        </header>

        <div className="px-5 py-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="px-3 py-2 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-200"
                onClick={() => sendMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {isOffline ? (
          <div className="px-5 py-2 bg-amber-100 text-amber-700 text-xs">الاتصال غير متوفر، سيتم إرسال الرسائل عند استعادة الشبكة.</div>
        ) : null}

        <div ref={containerRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-sm text-slate-500 mt-10">
              ابدأ المحادثة بطلب من الاقتراحات السريعة أعلاه.
            </div>
          ) : (
            messages.map((message) => <MessageBubble key={message.id} message={message} />)
          )}
          {streaming ? (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-primary-500 animate-ping" />
              جارٍ كتابة الرد...
            </div>
          ) : null}
          {error ? <div className="text-xs text-rose-500">{error}</div> : null}
        </div>

        {suggestions.length ? (
          <div className="border-t border-slate-200 dark:border-slate-800 px-5 py-4 bg-white/60 dark:bg-slate-900/40">
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100 mb-3">اقتراحات ذكية</h3>
            <div className="grid gap-3">
              {suggestions.map((item) => (
                <ActionCard key={item.title} title={item.title} description={item.body} actionName={item.action} />
              ))}
            </div>
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="border-t border-slate-200 dark:border-slate-800 px-5 py-4 bg-white dark:bg-slate-950">
          <div className="flex items-end gap-3">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={2}
              placeholder="اسألني عن الفواتير، المقيمين، الصيانة..."
              className="flex-1 resize-none rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              type="submit"
              disabled={streaming}
              className={clsx(
                'inline-flex items-center justify-center rounded-full px-4 py-3 text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-40',
                streaming && 'cursor-not-allowed'
              )}
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>

      <AiSettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </aside>
  );
};

export default ChatPanel;
