import { FormEvent, useEffect, useState } from 'react';

const STORAGE_KEY = 'mouqarr-settings';

interface SettingsState {
  organization: string;
  reminderHour: string;
  telegramWebhook: string;
  emailSender: string;
}

const SettingsPage = () => {
  const [state, setState] = useState<SettingsState>({ organization: '', reminderHour: '08:00', telegramWebhook: '', emailSender: '' });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setState(JSON.parse(stored));
    }
  }, []);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800">إعدادات المنصة</h2>
      <p className="text-sm text-slate-500 mt-1">قم بتعديل معلومات المؤسسة وقنوات التنبيه.</p>
      <form onSubmit={handleSubmit} className="mt-6 grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          <span>اسم المؤسسة</span>
          <input
            value={state.organization}
            onChange={(event) => setState((prev) => ({ ...prev, organization: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2"
            placeholder="شركة إدارة مجمع الرياض"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          <span>موعد التذكير اليومي</span>
          <input
            type="time"
            value={state.reminderHour}
            onChange={(event) => setState((prev) => ({ ...prev, reminderHour: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          <span>رابط ويب هوك تيليجرام</span>
          <input
            value={state.telegramWebhook}
            onChange={(event) => setState((prev) => ({ ...prev, telegramWebhook: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2"
            placeholder="https://api.telegram.org/bot..."
          />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          <span>مرسل البريد الإلكتروني</span>
          <input
            value={state.emailSender}
            onChange={(event) => setState((prev) => ({ ...prev, emailSender: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2"
            placeholder="alerts@mouqarr.app"
          />
        </label>
        <button
          type="submit"
          className="md:col-span-2 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white"
        >
          حفظ الإعدادات
        </button>
        {saved ? <span className="text-xs text-emerald-600">تم حفظ الإعدادات محليًا.</span> : null}
      </form>
    </div>
  );
};

export default SettingsPage;
