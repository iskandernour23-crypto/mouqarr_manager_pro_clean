import { useState } from 'react';
import { SparklesIcon } from '@heroicons/react/24/outline';
import ChatPanel from './ChatPanel';

interface ChatDockProps {
  open?: boolean;
  onOpenChange?: (value: boolean) => void;
}

const ChatDock = ({ open: controlledOpen, onOpenChange }: ChatDockProps) => {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen ?? internalOpen;

  const setOpen = (value: boolean) => {
    if (controlledOpen === undefined) {
      setInternalOpen(value);
    }
    onOpenChange?.(value);
  };

  return (
    <div className="relative h-full">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-40 inline-flex items-center gap-2 rounded-full bg-primary-600 hover:bg-primary-700 text-white px-4 py-3 shadow-lg"
      >
        <SparklesIcon className="w-5 h-5" />
        <span className="text-sm font-semibold">مساعد المنصة الذكي</span>
      </button>
      <ChatPanel open={open} onClose={() => setOpen(false)} />
    </div>
  );
};

export default ChatDock;
