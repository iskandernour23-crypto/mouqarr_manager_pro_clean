import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import remarkGfm from 'remark-gfm';
import { AiMessage } from '../../../store/ai';

interface MessageBubbleProps {
  message: AiMessage;
}

const roleStyles: Record<string, string> = {
  user: 'bg-primary-600 text-white self-end rounded-tl-3xl rounded-tr-md rounded-bl-3xl',
  assistant: 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700',
  tool: 'bg-emerald-50 dark:bg-emerald-900/40 border border-emerald-200 dark:border-emerald-700 text-emerald-900 dark:text-emerald-50',
  system: 'bg-slate-100 text-slate-700 dark:bg-slate-900/60 dark:text-slate-100',
};

const MessageBubble = memo(({ message }: MessageBubbleProps) => {
  const style = roleStyles[message.role] ?? roleStyles.assistant;
  return (
    <div className={clsx('flex flex-col space-y-2 max-w-full', message.role === 'user' ? 'items-end' : 'items-start')}>
      <div
        className={clsx(
          'rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm w-full md:max-w-[85%] whitespace-pre-wrap break-words',
          style
        )}
      >
        {message.pending && (
          <span className="inline-flex items-center text-xs font-semibold text-amber-600 mr-2">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse mr-1" />
            قيد الانتظار
          </span>
        )}
        <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-sm max-w-none prose-headings:font-semibold prose-pre:bg-slate-900 prose-pre:text-white">
          {message.content || '...'}
        </ReactMarkdown>
      </div>
      {message.attachments?.length ? (
        <div className="grid gap-2 w-full md:max-w-[80%]">
          {message.attachments.map((attachment) => (
            <div key={attachment.id} className="border border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-3 text-xs text-slate-600 dark:text-slate-200">
              <h5 className="font-semibold mb-1">{attachment.label}</h5>
              <p className="leading-5 whitespace-pre-wrap">{attachment.body}</p>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;
