import { useAiStore } from '../../../store/ai';

interface ActionCardProps {
  title: string;
  description: string;
  actionName?: string;
  params?: Record<string, unknown>;
}

const ActionCard = ({ title, description, actionName, params }: ActionCardProps) => {
  const runAction = useAiStore((state) => state.runAction);

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm">
      <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">{title}</h4>
      <p className="text-xs text-slate-600 dark:text-slate-300 mb-4 leading-5">{description}</p>
      {actionName ? (
        <button
          type="button"
          onClick={() => runAction(actionName, params ?? {})}
          className="inline-flex items-center px-3 py-2 rounded-full bg-primary-600 text-white text-xs font-semibold hover:bg-primary-700"
        >
          تنفيذ فوري
        </button>
      ) : null}
    </div>
  );
};

export default ActionCard;
