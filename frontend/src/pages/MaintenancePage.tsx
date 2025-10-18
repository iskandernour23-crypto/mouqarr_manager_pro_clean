import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';

interface Ticket {
  id: number;
  asset_id?: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: number;
  due_date?: string;
}

interface Option {
  id: number;
  label: string;
}

const priorities = [
  { value: 'high', label: 'عالية' },
  { value: 'medium', label: 'متوسطة' },
  { value: 'low', label: 'منخفضة' }
];

const MaintenancePage = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [assets, setAssets] = useState<Option[]>([]);
  const [supervisors, setSupervisors] = useState<Option[]>([]);
  const [form, setForm] = useState({
    asset_id: '',
    title: '',
    description: '',
    priority: 'medium',
    due_date: ''
  });

  const loadData = async () => {
    const [ticketRes, assetRes, supRes] = await Promise.all([
      api.get<Ticket[]>('/maintenance'),
      api.get<any[]>('/assets'),
      api.get<any[]>('/supervisors')
    ]);
    setTickets(ticketRes);
    setAssets(assetRes.map((item: any) => ({ id: item.id, label: item.name })));
    setSupervisors(supRes.map((item: any) => ({ id: item.id, label: item.user.name })));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.title) return;
    await api.post('/maintenance', {
      asset_id: form.asset_id ? Number(form.asset_id) : null,
      title: form.title,
      description: form.description,
      priority: form.priority,
      due_date: form.due_date || null
    });
    setForm({ asset_id: '', title: '', description: '', priority: 'medium', due_date: '' });
    loadData();
  };

  const assignTicket = async (ticketId: number, supervisorId?: number) => {
    if (!supervisorId) return;
    await api.post(`/maintenance/${ticketId}/assign/${supervisorId}`);
    loadData();
  };

  const closeTicket = async (ticketId: number) => {
    await api.put(`/maintenance/${ticketId}`, { status: 'closed' });
    loadData();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">تذكرة صيانة جديدة</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-5">
          <select
            value={form.asset_id}
            onChange={(event) => setForm((prev) => ({ ...prev, asset_id: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="">الأصل المرتبط (اختياري)</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.label}
              </option>
            ))}
          </select>
          <input
            value={form.title}
            onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
            placeholder="عنوان التذكرة"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.description}
            onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
            placeholder="وصف مختصر"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <select
            value={form.priority}
            onChange={(event) => setForm((prev) => ({ ...prev, priority: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            {priorities.map((priority) => (
              <option key={priority.value} value={priority.value}>
                {priority.label}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={form.due_date}
            onChange={(event) => setForm((prev) => ({ ...prev, due_date: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <button
            type="submit"
            className="md:col-span-5 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white"
          >
            إنشاء التذكرة
          </button>
        </form>
      </section>

      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">التذاكر الحالية</h2>
        <div className="mt-4 grid gap-3">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="rounded-2xl border border-slate-200 px-5 py-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{ticket.title}</p>
                  <p className="text-xs text-slate-500">الأولوية: {ticket.priority}</p>
                  <p className="text-xs text-slate-400">الحالة الحالية: {ticket.status}</p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={ticket.assigned_to ?? ''}
                    onChange={(event) => assignTicket(ticket.id, event.target.value ? Number(event.target.value) : undefined)}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-xs"
                  >
                    <option value="">إسناد مشرف</option>
                    {supervisors.map((supervisor) => (
                      <option key={supervisor.id} value={supervisor.id}>
                        {supervisor.label}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => closeTicket(ticket.id)}
                    className="rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-600"
                  >
                    إغلاق
                  </button>
                </div>
              </div>
              {ticket.due_date ? <p className="mt-2 text-xs text-slate-500">الاستحقاق: {ticket.due_date}</p> : null}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default MaintenancePage;
